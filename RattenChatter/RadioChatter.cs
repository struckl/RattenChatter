using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using HarmonyLib;
using UnityEngine;

namespace RattenChatter;

/// <summary>One transmission: a clip plus how long the net stays quiet before it.</summary>
internal sealed class ChatterLine
{
    public AudioClip Clip;
    public float GapBefore;
}

/// <summary>An exchange between two or more voices, played in order.</summary>
internal sealed class Conversation
{
    public string Id;
    public readonly List<ChatterLine> Lines = new List<ChatterLine>();
}

/// <summary>
/// Ambient radio chatter while flying. Clips are grouped into conversations and
/// played back with the pacing the generator recorded for them, so a snap
/// "Two." answers straight away while "stand by" leaves a real gap.
///
/// Conversations are drawn from a shuffle bag rather than picked at random, so
/// you hear all of them before any repeats. Between them the net goes quiet for
/// a random stretch — except now and then it stays busy and a second exchange
/// starts almost immediately, the way a real net comes in waves.
/// </summary>
internal static class RadioChatter
{
    // Used only when there is no manifest to read pacing from.
    private const float FallbackMinGap = 0.8f;
    private const float FallbackMaxGap = 1.8f;
    // How long to wait before retrying when something else is talking.
    private const float WarningBackoffSeconds = 5f;
    // Mid-conversation we poll often so the reply lands as soon as the warning
    // finishes instead of leaving an unnatural hole in the exchange.
    private const float MidConversationBackoffSeconds = 0.4f;
    // Gaps get a little wobble each replay so a conversation you have heard
    // before does not play back with identical timing.
    private const float GapJitterMin = 0.85f;
    private const float GapJitterMax = 1.25f;

    private static readonly List<Conversation> Conversations = new List<Conversation>();
    private static readonly List<int> Bag = new List<int>();
    private static Aircraft aircraft;
    private static float nextLineTime;
    private static Conversation current;
    private static int lineIndex;

    public static IEnumerator LoadAsync()
    {
        string chatterPath = Path.Combine(Plugin.AssetsPath, "chatter");
        if (!Directory.Exists(chatterPath))
        {
            Plugin.Logger.LogWarning($"No chatter assets found at '{chatterPath}'.");
            yield break;
        }

        string manifestPath = Path.Combine(chatterPath, "manifest.txt");
        if (File.Exists(manifestPath))
            yield return LoadFromManifest(manifestPath);
        else
            yield return LoadFromFileNames(chatterPath);

        int lines = 0;
        foreach (Conversation conversation in Conversations)
            lines += conversation.Lines.Count;
        Plugin.Logger.LogInfo(
            $"Loaded {Conversations.Count} chatter conversations ({lines} transmissions).");
    }

    /// <summary>
    /// Reads "conversation|file|gapBefore" rows written by
    /// tools/generate_chatter.py. Row order is the playback order.
    /// </summary>
    private static IEnumerator LoadFromManifest(string manifestPath)
    {
        Conversation conversation = null;
        foreach (string raw in File.ReadAllLines(manifestPath))
        {
            string row = raw.Trim();
            if (row.Length == 0 || row[0] == '#')
                continue;

            string[] parts = row.Split('|');
            if (parts.Length < 3)
            {
                Plugin.Logger.LogWarning($"Skipping malformed manifest row: '{row}'");
                continue;
            }
            if (!float.TryParse(parts[2], NumberStyles.Float, CultureInfo.InvariantCulture,
                    out float gap))
                gap = FallbackMinGap;

            if (conversation == null || conversation.Id != parts[0])
            {
                conversation = new Conversation { Id = parts[0] };
                Conversations.Add(conversation);
            }

            Conversation target = conversation;
            float gapBefore = gap;
            yield return AudioLoader.LoadAsync(
                Path.Combine("chatter", parts[1]),
                clip => target.Lines.Add(new ChatterLine { Clip = clip, GapBefore = gapBefore }));
        }
        Conversations.RemoveAll(c => c.Lines.Count == 0);
    }

    /// <summary>
    /// Fallback for hand-dropped clips with no manifest: "chatter01a" and
    /// "chatter01b" belong to conversation "chatter01", the last character
    /// orders the lines, and gaps are random.
    /// </summary>
    private static IEnumerator LoadFromFileNames(string chatterPath)
    {
        List<string> files = new List<string>(Directory.GetFiles(chatterPath, "*.mp3"));
        files.Sort();

        var grouped = new SortedDictionary<string, Conversation>();
        var order = new List<Conversation>();
        foreach (string file in files)
        {
            string name = Path.GetFileNameWithoutExtension(file);
            if (name.Length < 2)
                continue;
            string key = name.Substring(0, name.Length - 1);
            if (!grouped.TryGetValue(key, out Conversation conversation))
            {
                conversation = new Conversation { Id = key };
                grouped[key] = conversation;
                order.Add(conversation);
            }

            Conversation target = conversation;
            yield return AudioLoader.LoadAsync(
                Path.Combine("chatter", Path.GetFileName(file)),
                clip => target.Lines.Add(new ChatterLine
                {
                    Clip = clip,
                    GapBefore = Random.Range(FallbackMinGap, FallbackMaxGap),
                }));
        }
        foreach (Conversation conversation in order)
        {
            if (conversation.Lines.Count > 0)
                Conversations.Add(conversation);
        }
    }

    public static void SetAircraft(Aircraft newAircraft)
    {
        aircraft = newAircraft;
        current = null;
        ScheduleNextConversation(0f);
    }

    public static void Tick()
    {
        if (!Plugin.Enabled.Value || Conversations.Count == 0
            || aircraft == null || aircraft.disabled)
            return;
        if (Time.unscaledTime < nextLineTime)
            return;

        // Never talk over a voice warning, whether that means holding off the
        // start of an exchange or pausing partway through one.
        if (InterfaceAudio.IsBusy)
        {
            nextLineTime = Time.unscaledTime + (current == null
                ? WarningBackoffSeconds
                : MidConversationBackoffSeconds);
            return;
        }

        if (current == null)
        {
            current = NextConversation();
            lineIndex = 0;
        }

        ChatterLine line = current.Lines[lineIndex];
        InterfaceAudio.PlayOneShot(line.Clip, Plugin.Volume.Value);
        lineIndex++;

        if (lineIndex >= current.Lines.Count)
        {
            current = null;
            ScheduleNextConversation(line.Clip.length);
        }
        else
        {
            float gap = current.Lines[lineIndex].GapBefore
                * Random.Range(GapJitterMin, GapJitterMax);
            nextLineTime = Time.unscaledTime + line.Clip.length + gap;
        }
    }

    /// <summary>
    /// Draws from a shuffle bag so every conversation gets played once before
    /// any of them comes round again.
    /// </summary>
    private static Conversation NextConversation()
    {
        if (Bag.Count == 0)
        {
            for (int i = 0; i < Conversations.Count; i++)
                Bag.Add(i);
            // Fisher-Yates.
            for (int i = Bag.Count - 1; i > 0; i--)
            {
                int j = Random.Range(0, i + 1);
                (Bag[i], Bag[j]) = (Bag[j], Bag[i]);
            }
        }
        int last = Bag.Count - 1;
        int index = Bag[last];
        Bag.RemoveAt(last);
        return Conversations[index];
    }

    private static void ScheduleNextConversation(float clipLength)
    {
        // Now and then the net stays busy and the next exchange starts almost
        // on top of the last one. Real radio traffic clumps like that, and it
        // breaks up the metronome feel of one conversation per fixed pause.
        float pause = Random.value < Plugin.BusyNetChance.Value
            ? Random.Range(1.5f, 5f)
            : Random.Range(Plugin.MinPauseSeconds.Value, Plugin.MaxPauseSeconds.Value);
        nextLineTime = Time.unscaledTime + clipLength + pause;
    }
}

[HarmonyPatch(typeof(CombatHUD), "SetAircraft")]
internal static class RadioChatterAircraftPatch
{
    private static void Postfix(Aircraft aircraft)
    {
        RadioChatter.SetAircraft(aircraft);
    }
}

using System.IO;
using HarmonyLib;
using UnityEngine;
using UnityEngine.Networking;

namespace RattenChatter;

/// <summary>Loads audio clips from the plugin's Assets folder.</summary>
internal static class AudioLoader
{
    public static AudioClip Load(string fileName)
    {
        string path = Path.Combine(Plugin.AssetsPath, fileName);
        using var request = UnityWebRequestMultimedia.GetAudioClip($"file://{path}", AudioType.MPEG);
        request.SendWebRequest();
        while (!request.isDone)
        {
            // Busy-wait is acceptable here: only runs once during plugin startup
            // and the files are small local reads.
        }

        if (request.result != UnityWebRequest.Result.Success)
        {
            Plugin.Logger.LogError($"Failed to load audio clip '{path}': {request.error}");
            return null;
        }
        return DownloadHandlerAudioClip.GetContent(request);
    }
}

/// <summary>Plays clips on the game's interface audio source with a volume boost.</summary>
internal static class InterfaceAudio
{
    private static readonly AccessTools.FieldRef<SoundManager, AudioSource> InterfaceSource =
        AccessTools.FieldRefAccess<SoundManager, AudioSource>("interfaceSource");

    /// <summary>
    /// True while anything is talking on the interface source — the game's own
    /// audio or another mod's voice warnings (Bitching Ratte plays here too).
    /// Chatter uses this to stay out of the way instead of talking over a warning.
    /// </summary>
    public static bool IsBusy
    {
        get
        {
            if (SoundManager.i == null)
                return false;
            AudioSource source = InterfaceSource(SoundManager.i);
            return source != null && source.isPlaying;
        }
    }

    public static void PlayOneShot(AudioClip clip, float volume = 1f)
    {
        if (clip == null || SoundManager.i == null)
            return;
        InterfaceSource(SoundManager.i).PlayOneShot(clip, volume);
    }
}

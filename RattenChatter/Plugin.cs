using System.IO;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;

namespace RattenChatter;

[BepInPlugin(Guid, Name, Version)]
public class Plugin : BaseUnityPlugin
{
    public const string Guid = "dev.sewerlabs.rattenchatter";
    public const string Name = "Ratten Chatter";
    public const string Version = "1.0.0";

    internal static new ManualLogSource Logger;
    internal static string AssetsPath;

    internal static ConfigEntry<bool> Enabled;
    internal static ConfigEntry<float> Volume;
    internal static ConfigEntry<float> MinPauseSeconds;
    internal static ConfigEntry<float> MaxPauseSeconds;
    internal static ConfigEntry<float> BusyNetChance;

    private void Awake()
    {
        Logger = base.Logger;
        AssetsPath = Path.Combine(Paths.PluginPath, "RattenChatter", "Assets");

        BindConfig();
        new Harmony(Guid).PatchAll();
        if (Enabled.Value)
            StartCoroutine(RadioChatter.LoadAsync());

        Logger.LogInfo($"{Name} {Version} loaded.");
    }

    private void Update()
    {
        RadioChatter.Tick();
    }

    private void BindConfig()
    {
        Enabled = Config.Bind(
            "1. General", "Enable mod", true,
            "Master switch for the whole mod. On: quiet background radio chatter plays "
            + "while you fly. Off: silence. Note: if this was off when the game started, "
            + "turning it on needs a game restart (the audio is only loaded at startup); "
            + "turning it off works immediately.");
        Volume = Config.Bind(
            "1. General", "Volume", 1.2f,
            new ConfigDescription(
                "How loud the chatter is. 1 = same volume as the game's other cockpit "
                + "sounds, 2 = twice as loud, 0.5 = half as loud.",
                new AcceptableValueRange<float>(0f, 3f)));
        MinPauseSeconds = Config.Bind(
            "2. Timing", "Shortest pause (seconds)", 12f,
            "After one conversation ends, the radio stays quiet for a random time "
            + "between 'Shortest pause' and 'Longest pause' before the next one starts.");
        MaxPauseSeconds = Config.Bind(
            "2. Timing", "Longest pause (seconds)", 45f,
            "The longest the radio stays quiet between two conversations.");
        BusyNetChance = Config.Bind(
            "2. Timing", "Busy radio chance", 0.2f,
            new ConfigDescription(
                "Chance that the next conversation starts right after the previous one "
                + "instead of waiting out the pause, so traffic comes in bursts like a "
                + "real radio net. 0 = never, 1 = always, 0.2 = 20% of conversations.",
                new AcceptableValueRange<float>(0f, 1f)));
    }
}

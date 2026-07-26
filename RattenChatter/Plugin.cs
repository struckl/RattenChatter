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
            "Radio Chatter", "Enabled", true,
            "Play ambient radio chatter in the background while flying.");
        Volume = Config.Bind(
            "Radio Chatter", "Volume", 1.2f,
            "Chatter volume relative to other interface audio (voice warnings play at 3.0).");
        MinPauseSeconds = Config.Bind(
            "Radio Chatter", "MinPauseSeconds", 12f,
            "Minimum silence between chatter conversations.");
        MaxPauseSeconds = Config.Bind(
            "Radio Chatter", "MaxPauseSeconds", 45f,
            "Maximum silence between chatter conversations.");
        BusyNetChance = Config.Bind(
            "Radio Chatter", "BusyNetChance", 0.2f,
            "Chance (0-1) that the next conversation starts within a few seconds "
            + "instead of after the usual pause, so traffic comes in waves.");
    }
}

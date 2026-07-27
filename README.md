# Ratten Chatter | Nuclear Option

Ambient radio chatter for
[Nuclear Option](https://store.steampowered.com/app/2168680/Nuclear_Option/),
so the cockpit never feels dead quiet.

Around seventy short conversations play quietly in the background while you fly
— check-ins, intercepts, SEAD calls, tanker joins, carrier approaches, a
nine-line from a forward air controller, a wingman who will not hold formation,
and the odd release authorisation you would rather not have overheard.

Every one is two people and two or three lines: two aircraft, or an aircraft and
a tower, or an aircraft and mission control. One call, one answer, maybe a
closing word. Short enough that you catch it without stopping what you were
doing, and never a crowd scene that pulls your attention out of the cockpit.

Every callsign has its own voice — around thirty of them across forty distinct
neural voices and a dozen accents — and every voice goes through a full radio
treatment: band-limited to a comms channel, compressed flat by the
transmitter's level control, dirtied with clipping, and buried in Rauschen —
a steady open-carrier hiss with a crackle of pops and ticks riding on top,
opening a fraction of a second before the mic click and closing with a squelch
tail. An AWACS with a real antenna sounds nothing like a forward air controller
on a handheld or a wingman at the edge of the map.

It is mixed to sit behind the aircraft rather than in front of it. Turn `Volume`
up if you want the net closer.

Pacing comes from the script rather than a fixed timer, so a snap "Two." lands
straight away while "stand by" leaves an actual gap. Conversations are drawn
from a shuffle bag — you hear all of them before any repeats — and now and then
the net stays busy and a second exchange starts on top of the last one instead
of after the usual silence, which is what a genuinely busy net sounds like.

Chatter holds off while something else is talking on the interface channel, so
it never steps on a voice warning from the game or from another mod, and it
pauses partway through an exchange rather than talking over one.

Extracted from [MKMods](https://github.com/struckl/MKModsNO) into its own
plugin so you can run the chatter without the rest of that mod.

## Installation

1. Install [BepInEx 5](https://github.com/BepInEx/BepInEx/releases) into the
   Nuclear Option game folder and launch the game once so it generates its
   folders.
2. Copy the `RattenChatter` folder from the release into
   `Nuclear Option/BepInEx/plugins/`, so you end up with:

   ```
   BepInEx/plugins/RattenChatter/RattenChatter.dll
   BepInEx/plugins/RattenChatter/Assets/chatter/*.mp3
   BepInEx/plugins/RattenChatter/Assets/chatter/manifest.txt
   ```

3. Launch the game. Config is written to
   `BepInEx/config/dev.sewerlabs.rattenchatter.cfg`.

Clips load in the background over the first few seconds after startup rather
than blocking the loading screen, so the net may be quiet for a moment on the
first flight.

## Configuration

Settings live under `1. General` (master switch, volume) and `2. Timing`
(pauses between conversations) and are editable in-game with
[ConfigurationManager](https://github.com/BepInEx/BepInEx.ConfigurationManager).

| Setting | Default | Description |
| --- | --- | --- |
| `Enable mod` | `true` | Master switch. Turning it on mid-game needs a restart; turning it off works immediately. |
| `Volume` | `1.2` | How loud the chatter is. `1` matches the game's other cockpit sounds; the clips are already mixed low, so raise this to bring the net forward. |
| `Shortest pause (seconds)` | `12` | Minimum silence between conversations. |
| `Longest pause (seconds)` | `45` | Maximum silence between conversations. |
| `Busy radio chance` | `0.2` | Chance the next conversation starts within a few seconds instead of after the usual pause, so traffic comes in waves. Set to `0` for evenly spaced chatter. |

## Adding your own chatter

The shipped voices are generated, and the whole pipeline is in
[`tools/`](tools/) — scripts, cast, text-to-speech and the radio filter chain.
See [tools/README.md](tools/README.md). Adding a conversation is a handful of
lines of dialogue plus one command, and that is also where the knobs for
loudness and how much Rauschen sits under the voice live.

If you would rather drop in your own recordings, the plugin reads clips two ways.

**With a manifest** (what the generator writes) — `Assets/chatter/manifest.txt`
lists one transmission per row as `conversation|file|gap`, where `gap` is the
seconds of dead air before that line. Row order is playback order:

```
chatter07|chatter07a.mp3|0.00
chatter07|chatter07b.mp3|1.40
chatter07|chatter07c.mp3|0.70
```

**Without one** — delete `manifest.txt` and clips are grouped by file name:
everything but the last character is the conversation key, the last character
orders the lines, and gaps are randomised between 0.8 and 1.8 seconds.

```
chatter13a.mp3   ->  conversation "chatter13", line 1
chatter13b.mp3   ->  conversation "chatter13", line 2
```

Either way the plugin goes quiet for a random time between `Shortest pause`
and `Longest pause` between conversations and works through all of them before
repeating.

## Building

Requires the .NET SDK and a local Nuclear Option install (the game assemblies
are referenced directly).

```bash
dotnet build RattenChatter.sln -c Release
```

The default game directory is `Y:\SteamLibrary\steamapps\common\Nuclear Option`
(set in `RattenChatter/RattenChatter.csproj`). Override it with:

```bash
dotnet build RattenChatter.sln -c Release -p:GameDirectory="D:\Steam\steamapps\common\Nuclear Option"
```

A successful build deploys the DLL and assets straight into
`<GameDirectory>/BepInEx/plugins/RattenChatter`.

## Credits

Radio chatter code, scripts and audio pipeline by Lukas Struckl. Voices are
Microsoft Edge neural voices via [edge-tts](https://github.com/rany2/edge-tts),
put through an [ffmpeg](https://ffmpeg.org/) radio chain. Built on
[BepInEx](https://github.com/BepInEx/BepInEx) and
[HarmonyX](https://github.com/BepInEx/HarmonyX). Originally part of
[MKMods](https://github.com/struckl/MKModsNO), a fork of
[mkualquiera/nuclear_option_modding](https://github.com/mkualquiera/nuclear_option_modding).

# Ratten Chatter

Ambient radio chatter for
[Nuclear Option](https://store.steampowered.com/app/2168680/Nuclear_Option/),
so the cockpit never feels dead quiet.

Short pilot/controller conversations play in the background while you fly —
check-ins, kill calls, landing clearances — separated by random pauses. Every
conversation uses a different pilot voice talking to a constant controller
voice, complete with squelch clicks and radio noise. Chatter holds off while
something else is talking on the interface channel, so it never steps on a
voice warning from the game or from another mod.

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
   ```

3. Launch the game. Config is written to
   `BepInEx/config/dev.sewerlabs.rattenchatter.cfg`.

## Configuration

All settings live under the `Radio Chatter` section and are editable in-game
with [ConfigurationManager](https://github.com/BepInEx/BepInEx.ConfigurationManager).

| Setting | Default | Description |
| --- | --- | --- |
| `Enabled` | `true` | Play ambient radio chatter while flying. |
| `Volume` | `1.2` | Chatter volume relative to other interface audio (voice warnings play at `3.0`). |
| `MinPauseSeconds` | `12` | Minimum silence between conversations. |
| `MaxPauseSeconds` | `45` | Maximum silence between conversations. |

## Adding your own chatter

Drop MP3 files into `Assets/chatter/`. The file name decides how they are
grouped into conversations: everything but the last character is the
conversation key, the last character orders the lines within it.

```
chatter13a.mp3   ->  conversation "chatter13", line 1
chatter13b.mp3   ->  conversation "chatter13", line 2
chatter13c.mp3   ->  conversation "chatter13", line 3
```

Lines play in order with a short 0.8–1.8 s radio pause between them, then the
plugin goes quiet for a random `MinPauseSeconds`–`MaxPauseSeconds` before
picking a different conversation.

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

Radio chatter code and voice assets by Lukas Struckl. Built on
[BepInEx](https://github.com/BepInEx/BepInEx) and
[HarmonyX](https://github.com/BepInEx/HarmonyX). Originally part of
[MKMods](https://github.com/struckl/MKModsNO), a fork of
[mkualquiera/nuclear_option_modding](https://github.com/mkualquiera/nuclear_option_modding).

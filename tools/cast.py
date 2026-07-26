"""The voice cast for Ratten Chatter.

Every callsign gets its own neural voice plus a fixed set of quirks (speaking
rate, pitch offset, radio profile), so a callsign sounds like the same person
every time it comes up and never like the pilot two conversations ago.

Voices come from Microsoft Edge's neural TTS (the `edge-tts` package): free, no
API key, and far less robotic than SAPI. Accents are spread on purpose — a
coalition net is not staffed by twenty identical Americans.

Radio profiles (see RADIO_PROFILES in generate_chatter.py):
  near    strong signal, close aircraft
  far     weak, thin, hissy — someone at the edge of the map
  ground  handheld / vehicle set, tinny and compressed
  ground_far  handheld at range, rough
  station  ground station or AWACS with a real antenna: clean and loud
  cockpit_hot  shouting into the mask, clipping the transmitter
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Speaker:
    """One recurring character on the radio net."""

    voice: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    profile: str = "near"


# --------------------------------------------------------------------------
# Controllers, stations and support. These recur across many conversations,
# so their voices stay locked for continuity.
# --------------------------------------------------------------------------
STATIONS = {
    # BDF airborne early warning — the voice you hear most often.
    "MAGIC": Speaker("en-US-ChristopherNeural", rate="-4%", profile="station"),
    # Second AWACS track, different shift, different person.
    "SENTRY": Speaker("en-US-AriaNeural", rate="-2%", pitch="-4Hz", profile="station"),
    # Ground controlled intercept, bored and flat.
    "WARDEN": Speaker("en-US-SteffanNeural", rate="-7%", pitch="-8Hz", profile="station"),
    "MARIS TOWER": Speaker("en-GB-ThomasNeural", rate="-2%", profile="station"),
    "MARIS GROUND": Speaker("en-GB-LibbyNeural", rate="+2%", profile="station"),
    "AGRAPOL TOWER": Speaker("en-AU-WilliamMultilingualNeural", rate="-3%", profile="station"),
    "SANDRIFT TOWER": Speaker("en-IN-PrabhatNeural", rate="-4%", profile="station"),
    "OPAL APPROACH": Speaker("en-CA-ClaraNeural", rate="-1%", profile="station"),
    # Carrier air traffic control.
    "HYPERION": Speaker("en-US-EricNeural", rate="-5%", pitch="-6Hz", profile="station"),
    "PADDLES": Speaker("en-US-RogerNeural", rate="+6%", profile="station"),
    # Tanker crew — relaxed, they have coffee up there.
    "TEXACO": Speaker("en-US-GuyNeural", rate="-6%", pitch="-10Hz", profile="near"),
    # Search and rescue.
    "LIFEGUARD": Speaker("en-IE-EmilyNeural", rate="+3%", profile="near"),
    # Forward air controller on the ground, handheld radio.
    "SLEDGE": Speaker("en-ZA-LukeNeural", rate="+4%", profile="ground"),
    "OUTLAW": Speaker("en-US-BrianMultilingualNeural", rate="+2%", profile="ground"),
    # Armour and logistics on the ground net, bleeding over.
    "IRONHIDE": Speaker("en-PH-JamesNeural", rate="+1%", profile="ground_far"),
    "MULE": Speaker("en-NG-AbeoNeural", rate="-2%", profile="ground_far"),
    # Naval.
    "DYNAMO": Speaker("en-SG-WayneNeural", rate="-4%", profile="station"),
    # Command authority. Slow, deliberate, unpleasant to listen to.
    "KEYSTONE": Speaker("en-US-AndrewMultilingualNeural", rate="-12%", pitch="-14Hz", profile="station"),
}

# --------------------------------------------------------------------------
# Aircrew. One voice each, spread across accents and both genders.
# --------------------------------------------------------------------------
AIRCREW = {
    "RAZOR ONE": Speaker("en-US-AndrewNeural", rate="-2%", pitch="-6Hz"),
    "RAZOR TWO": Speaker("en-US-BrianNeural", rate="+3%"),
    "VIPER ONE": Speaker("en-GB-RyanNeural", rate="-1%", pitch="-4Hz"),
    "VIPER TWO": Speaker("en-GB-SoniaNeural", rate="+4%"),
    "HAMMER ONE": Speaker("en-US-JennyNeural", rate="+1%", pitch="-3Hz"),
    "HAMMER THREE": Speaker("en-CA-LiamNeural", rate="+2%"),
    "CHISEL ONE": Speaker("en-NZ-MitchellNeural", rate="-3%", pitch="-5Hz"),
    "CHISEL TWO": Speaker("en-NZ-MollyNeural", rate="+5%", profile="far"),
    "LONGBOW": Speaker("en-IE-ConnorNeural", rate="-2%"),
    "WIDOW ONE": Speaker("en-US-AvaMultilingualNeural", rate="+2%", pitch="-2Hz"),
    "WIDOW TWO": Speaker("en-ZA-LeahNeural", rate="+3%"),
    "STINGER": Speaker("en-US-EmmaMultilingualNeural", rate="+4%"),
    "TALON ONE": Speaker("en-AU-NatashaNeural", rate="+1%", pitch="-3Hz"),
    "TALON FOUR": Speaker("en-CA-LiamNeural", rate="+7%", pitch="+8Hz", profile="cockpit_hot"),
    "BADGER": Speaker("en-US-MichelleNeural", rate="-3%", pitch="-5Hz"),
    "KESTREL ONE": Speaker("en-GB-ThomasNeural", rate="+5%", pitch="+6Hz"),
    "KESTREL TWO": Speaker("en-HK-SamNeural", rate="+2%"),
    "GHOST": Speaker("en-US-EmmaNeural", rate="-6%", pitch="-6Hz", profile="far"),
    "DAGGER ONE": Speaker("en-KE-ChilembaNeural", rate="-1%"),
    "DAGGER TWO": Speaker("en-PH-RosaNeural", rate="+4%"),
    "ANVIL ONE": Speaker("en-US-AriaNeural", rate="+2%", pitch="+4Hz", profile="cockpit_hot"),
    "RHINO": Speaker("en-ZA-LukeNeural", rate="-4%", pitch="-8Hz", profile="near"),
    "SABRE ONE": Speaker("en-IE-ConnorNeural", rate="+6%", pitch="+7Hz", profile="cockpit_hot"),
    "JACKAL": Speaker("en-SG-LunaNeural", rate="+3%"),
    "COWBOY": Speaker("en-US-RogerNeural", rate="+8%", pitch="+4Hz"),
    "PELICAN": Speaker("en-TZ-ElimuNeural", rate="-5%", pitch="-6Hz"),
    "SPADE": Speaker("en-GB-MaisieNeural", rate="+2%", profile="far"),
    "TUSK": Speaker("en-IN-PrabhatNeural", rate="+3%", pitch="+3Hz"),
    "MOTH": Speaker("en-KE-AsiliaNeural", rate="+1%", profile="far"),
    "SHEPHERD": Speaker("en-US-ChristopherNeural", rate="+4%", pitch="+6Hz"),
}

CAST = {**STATIONS, **AIRCREW}

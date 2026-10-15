"""The voice cast for Ratten Chatter.

Every callsign is one person, so it sounds the same every time it comes up and
never like the pilot two conversations ago. Each entry carries two voices, one
per engine in generate_chatter.py:

  vctk     the default (Chatterbox) engine: a real speaker from the CSTR VCTK
           Corpus (CC BY 4.0) that Chatterbox clones from a ~12 s reference.
           One speaker per callsign — no two callsigns share a person. The
           comment after each entry is the speaker's accent and region from
           vctk/speaker-info.txt.
  voice    the edge-tts fallback: a Microsoft Edge neural voice, with `rate`
           and `pitch` offsets so the callsigns that share one still differ.
           Chatterbox ignores rate and pitch; a real person already has their
           own.

Accents are spread on purpose — a coalition net is not staffed by twenty
identical Americans. VCTK is mostly British and Irish, so the cast leans that
way where edge-tts had Kenyan, Nigerian, Filipino or Singaporean voices. It
only has 47 men, 30 of whom are already Sea Power Radio's voices; the 16 left
are used here first, and the American, Canadian, Australian and Irish men —
there are no spare ones — are shared with that mod.

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
    vctk: str = ""


# --------------------------------------------------------------------------
# Controllers, stations and support. These recur across many conversations,
# so their voices stay locked for continuity.
# --------------------------------------------------------------------------
STATIONS = {
    # BDF airborne early warning — the voice you hear most often.
    "MAGIC": Speaker("en-US-ChristopherNeural", rate="-4%", profile="station", vctk="p360"),  # American, New Jersey
    # Second AWACS track, different shift, different person.
    "SENTRY": Speaker("en-US-AriaNeural", rate="-2%", pitch="-4Hz", profile="station", vctk="p300"),  # American, California
    # Ground controlled intercept, bored and flat.
    "WARDEN": Speaker("en-US-SteffanNeural", rate="-7%", pitch="-8Hz", profile="station", vctk="p311"),  # American, Iowa
    "MARIS TOWER": Speaker("en-GB-ThomasNeural", rate="-2%", profile="station", vctk="p258"),  # English, Southern England
    "MARIS GROUND": Speaker("en-GB-LibbyNeural", rate="+2%", profile="station", vctk="p228"),  # English, Southern England
    "AGRAPOL TOWER": Speaker("en-AU-WilliamMultilingualNeural", rate="-3%", profile="station", vctk="p374"),  # Australian
    "SANDRIFT TOWER": Speaker("en-IN-PrabhatNeural", rate="-4%", profile="station", vctk="p376"),  # Indian
    "OPAL APPROACH": Speaker("en-CA-ClaraNeural", rate="-1%", profile="station", vctk="p307"),  # Canadian, Ontario
    # Carrier air traffic control.
    "HYPERION": Speaker("en-US-EricNeural", rate="-5%", pitch="-6Hz", profile="station", vctk="p345"),  # American, Florida
    "PADDLES": Speaker("en-US-RogerNeural", rate="+6%", profile="station", vctk="p334"),  # American, Chicago
    # Tanker crew — relaxed, they have coffee up there.
    "TEXACO": Speaker("en-US-GuyNeural", rate="-6%", pitch="-10Hz", profile="near", vctk="p316"),  # Canadian, Alberta
    # Search and rescue.
    "LIFEGUARD": Speaker("en-IE-EmilyNeural", rate="+3%", profile="near", vctk="p288"),  # Irish, Dublin
    # Forward air controller on the ground, handheld radio.
    "SLEDGE": Speaker("en-ZA-LukeNeural", rate="+4%", profile="ground", vctk="p347"),  # South African, Johannesburg
    "OUTLAW": Speaker("en-US-BrianMultilingualNeural", rate="+2%", profile="ground", vctk="p302"),  # Canadian, Montreal
    # Armour and logistics on the ground net, bleeding over.
    "IRONHIDE": Speaker("en-PH-JamesNeural", rate="+1%", profile="ground_far", vctk="p247"),  # Scottish, Argyll
    "MULE": Speaker("en-NG-AbeoNeural", rate="-2%", profile="ground_far", vctk="p255"),  # Scottish, Galloway
    # Naval.
    "DYNAMO": Speaker("en-SG-WayneNeural", rate="-4%", profile="station", vctk="p273"),  # English, Suffolk
    # Command authority. Slow, deliberate, unpleasant to listen to.
    "KEYSTONE": Speaker("en-US-AndrewMultilingualNeural", rate="-12%", pitch="-14Hz", profile="station", vctk="p254"),  # English, Surrey
}

# --------------------------------------------------------------------------
# Aircrew. One voice each, spread across accents and both genders.
# --------------------------------------------------------------------------
AIRCREW = {
    "RAZOR ONE": Speaker("en-US-AndrewNeural", rate="-2%", pitch="-6Hz", vctk="p364"),  # Irish, Donegal
    "RAZOR TWO": Speaker("en-US-BrianNeural", rate="+3%", vctk="p271"),  # Scottish, Fife
    "VIPER ONE": Speaker("en-GB-RyanNeural", rate="-1%", pitch="-4Hz", vctk="p287"),  # English, York
    "VIPER TWO": Speaker("en-GB-SoniaNeural", rate="+4%", vctk="p229"),  # English, Southern England
    "HAMMER ONE": Speaker("en-US-JennyNeural", rate="+1%", pitch="-3Hz", vctk="p301"),  # American, North Carolina
    "HAMMER THREE": Speaker("en-CA-LiamNeural", rate="+2%", vctk="p363"),  # Canadian, Toronto
    "CHISEL ONE": Speaker("en-NZ-MitchellNeural", rate="-3%", pitch="-5Hz", vctk="p326"),  # Australian, Sydney
    "CHISEL TWO": Speaker("en-NZ-MollyNeural", rate="+5%", profile="far", vctk="p244"),  # English, Manchester
    "LONGBOW": Speaker("en-IE-ConnorNeural", rate="-2%", vctk="p241"),  # Scottish, Perth
    "WIDOW ONE": Speaker("en-US-AvaMultilingualNeural", rate="+2%", pitch="-2Hz", vctk="p305"),  # American, Philadelphia
    "WIDOW TWO": Speaker("en-ZA-LeahNeural", rate="+3%", vctk="p314"),  # South African, Cape Town
    "STINGER": Speaker("en-US-EmmaMultilingualNeural", rate="+4%", vctk="p333"),  # American, Indiana
    "TALON ONE": Speaker("en-AU-NatashaNeural", rate="+1%", pitch="-3Hz", vctk="p253"),  # Welsh, Cardiff
    "TALON FOUR": Speaker("en-CA-LiamNeural", rate="+7%", pitch="+8Hz", profile="cockpit_hot", vctk="p284"),  # Scottish, Fife
    "BADGER": Speaker("en-US-MichelleNeural", rate="-3%", pitch="-5Hz", vctk="p310"),  # American, Tennessee
    "KESTREL ONE": Speaker("en-GB-ThomasNeural", rate="+5%", pitch="+6Hz", vctk="p285"),  # Scottish, Edinburgh
    "KESTREL TWO": Speaker("en-HK-SamNeural", rate="+2%", vctk="p275"),  # Scottish, Midlothian
    "GHOST": Speaker("en-US-EmmaNeural", rate="-6%", pitch="-6Hz", profile="far", vctk="p339"),  # American, Pennsylvania
    "DAGGER ONE": Speaker("en-KE-ChilembaNeural", rate="-1%", vctk="p246"),  # Scottish, Selkirk
    "DAGGER TWO": Speaker("en-PH-RosaNeural", rate="+4%", vctk="p248"),  # Indian
    "ANVIL ONE": Speaker("en-US-AriaNeural", rate="+2%", pitch="+4Hz", profile="cockpit_hot", vctk="p361"),  # American, New Jersey
    "RHINO": Speaker("en-ZA-LukeNeural", rate="-4%", pitch="-8Hz", profile="near", vctk="p272"),  # Scottish, Edinburgh
    "SABRE ONE": Speaker("en-IE-ConnorNeural", rate="+6%", pitch="+7Hz", profile="cockpit_hot", vctk="p298"),  # Irish, Tipperary
    "JACKAL": Speaker("en-SG-LunaNeural", rate="+3%", vctk="p265"),  # Scottish, Ross
    "COWBOY": Speaker("en-US-RogerNeural", rate="+8%", pitch="+4Hz", vctk="p292"),  # Northern Irish, Belfast
    "PELICAN": Speaker("en-TZ-ElimuNeural", rate="-5%", pitch="-6Hz", vctk="p227"),  # English, Cumbria
    "SPADE": Speaker("en-GB-MaisieNeural", rate="+2%", profile="far", vctk="p239"),  # English, South West
    "TUSK": Speaker("en-IN-PrabhatNeural", rate="+3%", pitch="+3Hz", vctk="p251"),  # Indian
    "MOTH": Speaker("en-KE-AsiliaNeural", rate="+1%", profile="far", vctk="p238"),  # Northern Irish, Belfast
    "SHEPHERD": Speaker("en-US-ChristopherNeural", rate="+4%", pitch="+6Hz", vctk="p270"),  # English, Yorkshire
}

CAST = {**STATIONS, **AIRCREW}

"""
build_seasonal_data.py
Generates vassar_seasonal.json — seasonal "exciting moment" events for all 168
species on Vassar campus, calibrated to USDA zone 6b / Poughkeepsie NY.

Bloom dates anchored to USA-NPN median first-open-flower DOY for NY (queried
Apr 2026). Fall color anchored to NPN median >=50%-colored-leaves DOY for NY.
All other events (bark, fragrance, fruit, spring emergence) are curated.
"""

import json

# Each entry: list of event dicts with keys:
#   name        short label
#   type        bloom | fall_color | bark | fruit | foliage | fragrance
#   desc        one-sentence description shown in popup / panel
#   start       MM-DD (start of interesting window, inclusive)
#   end         MM-DD (end of window)
#   icon        emoji for the event type

# Icon/color helpers
ICONS = {
    "bloom":      "🌸",
    "fall_color": "🍂",
    "bark":       "🌳",
    "fruit":      "🍎",
    "foliage":    "🌿",
    "fragrance":  "✨",
}

def ev(name, etype, desc, start, end):
    return {"name": name, "type": etype, "desc": desc,
            "start": start, "end": end, "icon": ICONS[etype]}

# ─────────────────────────────────────────────────────────────────────────────
# SEASONAL EVENTS — keyed by common_name exactly as it appears in the CSV
# ─────────────────────────────────────────────────────────────────────────────
SEASONAL = {

    # ── WITCHHAZEL — blooms on bare branches in late fall / winter ──────────
    "Witchhazel": [
        ev("Late-fall bloom", "bloom",
           "Spidery yellow flowers appear on bare branches in late fall — one of the last trees to bloom",
           "10-15", "12-01"),
        ev("Golden fall color", "fall_color",
           "Leaves turn rich gold-yellow just as flowers begin to open",
           "10-15", "11-15"),
    ],

    # ── CORNELIAN CHERRY DOGWOOD — very early spring ────────────────────────
    "Dogwood-Cornelian Cherry": [
        ev("Early spring bloom", "bloom",
           "Tiny yellow flowers cover bare branches — one of the very first trees to bloom on campus",
           "03-05", "04-05"),
        ev("Bright red fruit", "fruit",
           "Glossy cherry-red oval fruits ripen, edible and bird-attracting",
           "07-15", "09-01"),
    ],

    # ── PUSSY WILLOW ─────────────────────────────────────────────────────────
    "Willow-Pussy": [
        ev("Silver catkins", "bloom",
           "Soft silver catkins emerge on bare branches — a classic early spring sight",
           "03-01", "04-15"),
    ],

    # ── MAGNOLIAS ────────────────────────────────────────────────────────────
    "Magnolia-Star": [
        ev("Star magnolia bloom", "bloom",
           "Masses of white star-shaped flowers open on bare branches — first magnolia to bloom",
           "03-25", "04-20"),
    ],
    "Magnolia-Saucer": [
        ev("Saucer magnolia bloom", "bloom",
           "Large pink-and-white saucer-shaped flowers on bare branches, one of spring's most spectacular shows",
           "04-01", "04-25"),
    ],
    "Magnolia": [
        ev("Magnolia bloom", "bloom",
           "Large fragrant flowers open before or with the emerging leaves",
           "04-05", "05-10"),
    ],
    "Magnolia-Sweetbay": [
        ev("Sweetbay magnolia bloom", "bloom",
           "Creamy white lemon-scented flowers bloom over a long season",
           "05-15", "06-30"),
    ],
    "Magnolia-Cucumbertree": [
        ev("Cucumbertree bloom", "bloom",
           "Pale yellow-green tulip-like flowers, subtle but distinctive",
           "04-20", "05-15"),
        ev("Cucumber-like fruits", "fruit",
           "Cucumber-shaped red-to-pink aggregate fruits are eye-catching in late summer",
           "08-15", "10-01"),
    ],
    "Magnolia-Bigleaf": [
        ev("Bigleaf magnolia bloom", "bloom",
           "Huge creamy white flowers up to 12\" across — among the largest of any hardy tree",
           "05-15", "06-15"),
    ],
    "Magnolia-Southern": [
        ev("Southern magnolia bloom", "bloom",
           "Large fragrant white flowers on an evergreen tree — dramatic all summer",
           "06-01", "07-15"),
    ],

    # ── SERVICEBERRIES ───────────────────────────────────────────────────────
    "Serviceberry": [
        ev("Spring bloom", "bloom",
           "Clouds of white star-shaped flowers — among the first trees to bloom after the magnolias",
           "04-15", "05-05"),
        ev("Edible blue-purple berries", "fruit",
           "Sweet blue-purple berries ripen — edible, loved by birds",
           "06-10", "07-10"),
        ev("Orange-red fall color", "fall_color",
           "Leaves turn vibrant orange and red",
           "10-01", "10-25"),
    ],
    "Serviceberry-Downy": [
        ev("Spring bloom", "bloom",
           "White flower clusters on bare branches — one of the earliest to bloom",
           "04-15", "05-05"),
        ev("Summer berries", "fruit",
           "Sweet edible blue-purple berries ripen",
           "06-10", "07-10"),
        ev("Orange-red fall color", "fall_color",
           "Vivid orange-red fall foliage",
           "10-01", "10-25"),
    ],

    # ── CHERRIES (NPN: Prunus serrulata bloom ~Apr 15–May 5) ─────────────────
    "Cherry-Yoshino": [
        ev("Pink-white bloom", "bloom",
           "Pale pink blooms smother the tree — one of the most celebrated spring-flowering cherries",
           "04-10", "05-01"),
    ],
    "Cherry-Kwanzan": [
        ev("Double-pink bloom", "bloom",
           "Double deep-pink pompom flowers are among the showiest of all flowering cherries",
           "04-15", "05-05"),
    ],
    "Cherry-Sargent": [
        ev("Deep-pink bloom", "bloom",
           "Rich deep-pink single flowers blanket the tree before the leaves open",
           "04-10", "04-30"),
        ev("Brilliant fall color", "fall_color",
           "Orange-red fall color comes exceptionally early",
           "09-20", "10-15"),
    ],
    "Cherry-Weeping": [
        ev("Cascading bloom", "bloom",
           "Weeping branches drip with pink or white flowers in a dramatic waterfall effect",
           "04-10", "04-30"),
    ],
    "Cherry-Flowering": [
        ev("Spring bloom", "bloom",
           "White or pink flowers densely cover the branches — a classic spring display",
           "04-15", "05-05"),
    ],
    "Cherry-Black": [
        ev("White flower clusters", "bloom",
           "Long racemes of small white flowers dangle from branches",
           "04-20", "05-15"),
        ev("Bird-magnet fruits", "fruit",
           "Small black cherries ripen — extremely attractive to birds",
           "07-15", "09-01"),
    ],
    "Cherry": [
        ev("Spring bloom", "bloom",
           "White or pink cherry blossoms brighten the landscape",
           "04-10", "05-05"),
    ],

    # ── REDBUD (NPN NY median bloom DOY 117 = Apr 26) ───────────────────────
    "Redbud-Eastern": [
        ev("Magenta bloom", "bloom",
           "Vivid magenta-pink flowers stud every branch and even the trunk before leaves appear",
           "04-20", "05-10"),
        ev("Yellow fall color", "fall_color",
           "Heart-shaped leaves turn clear yellow",
           "10-05", "10-25"),
        ev("Persistent seed pods", "fruit",
           "Flat maroon-brown bean pods hang attractively through winter",
           "10-01", "02-15"),
    ],

    # ── DOGWOODS (NPN NY median bloom DOY 122 = May 1) ───────────────────────
    "Dogwood-Flowering": [
        ev("White bract bloom", "bloom",
           "Large white four-bract flowers cover the tiered horizontal branches — campus classic",
           "04-20", "05-15"),
        ev("Scarlet fruit clusters", "fruit",
           "Glossy red berries in clusters appear — loved by migrating birds",
           "09-01", "10-15"),
        ev("Red-to-purple fall color", "fall_color",
           "Leaves turn deep scarlet-red, some tinged purple",
           "09-25", "10-20"),
    ],
    "Dogwood-Kousa": [
        ev("White star-like bloom", "bloom",
           "Four-pointed star-like white bracts appear after the leaves — later and longer-lasting than Flowering Dogwood",
           "05-20", "06-25"),
        ev("Raspberry-like fruits", "fruit",
           "Pink-red raspberry-textured fruits hang like ornaments — edible",
           "08-20", "10-01"),
        ev("Exfoliating bark", "bark",
           "With age, bark flakes into a puzzle-piece mosaic of tan, brown, and gray",
           "01-01", "12-31"),
    ],
    "Dogwood-Pagoda": [
        ev("White flower clusters", "bloom",
           "Flat clusters of small white flowers on strongly layered horizontal branches",
           "05-01", "05-25"),
        ev("Blue-black berries on red stalks", "fruit",
           "Blue-black berries on vivid red-pink stalks are ornamentally striking",
           "08-01", "09-30"),
    ],
    "Dogwood-Gray": [
        ev("White flower clusters", "bloom",
           "Flat clusters of small white flowers",
           "05-15", "06-15"),
    ],

    # ── PEAR-CALLERY ─────────────────────────────────────────────────────────
    "Pear-Callery": [
        ev("Early white bloom", "bloom",
           "Dense white flowers completely smother the tree — spectacular but briefly",
           "04-01", "04-20"),
        ev("Crimson-maroon fall color", "fall_color",
           "Brilliant crimson to purple-maroon fall color, often one of the best on campus",
           "10-15", "11-10"),
    ],

    # ── CRABAPPLES ───────────────────────────────────────────────────────────
    "Crabapple": [
        ev("Spring bloom", "bloom",
           "Masses of pink-to-white flowers smother the tree — one of spring's peak flowering moments",
           "04-15", "05-10"),
        ev("Persistent fruits", "fruit",
           "Small red, orange, or yellow fruits cling to branches through fall and winter",
           "09-15", "02-01"),
    ],
    "Crabapple-Flowering": [
        ev("Spring bloom", "bloom",
           "Dense clusters of pink or white fragrant flowers",
           "04-15", "05-10"),
        ev("Persistent fruits", "fruit",
           "Colorful small fruits persist through winter",
           "09-15", "02-01"),
    ],
    "Crabapple-Sargent": [
        ev("White bloom", "bloom",
           "Masses of pure white flowers — extremely floriferous",
           "04-20", "05-10"),
        ev("Bright red tiny fruits", "fruit",
           "Tiny bright-red fruits are persistent and very ornamental",
           "09-15", "02-01"),
    ],

    # ── HAWTHORNS ────────────────────────────────────────────────────────────
    "Hawthorn": [
        ev("White bloom", "bloom",
           "Clusters of white flowers with a distinctive aroma",
           "04-20", "05-15"),
        ev("Red or orange fruits", "fruit",
           "Small apple-like fruits persist into winter and attract birds",
           "09-15", "01-15"),
        ev("Orange-red fall color", "fall_color",
           "Foliage turns orange to red",
           "10-10", "11-01"),
    ],
    "Hawthorn-English": [
        ev("White bloom", "bloom",
           "Dense clusters of white flowers",
           "04-20", "05-15"),
        ev("Red haws persist", "fruit",
           "Bright red fruits cling through winter, attracting birds",
           "09-15", "01-15"),
    ],

    # ── APPLE ────────────────────────────────────────────────────────────────
    "Apple-Common": [
        ev("Pink-white bloom", "bloom",
           "Classic apple blossoms — fragrant pink-tinged white flowers",
           "04-15", "05-10"),
        ev("Fruits ripen", "fruit",
           "Apples color up and ripen",
           "08-15", "10-15"),
    ],

    # ── MAPLES ───────────────────────────────────────────────────────────────
    "Maple-Red": [
        ev("Red flower clusters", "bloom",
           "Tiny red flower clusters appear on bare branches — first maple to bloom, the harbinger of spring",
           "03-25", "04-20"),
        ev("Red fall color", "fall_color",
           "Brilliant red to orange-red fall color; often one of the first maples to turn",
           "09-25", "10-25"),
    ],
    "Maple-Sugar": [
        ev("Spring flowers", "bloom",
           "Yellowish flower clusters emerge just as the leaves unfold",
           "04-15", "05-05"),
        ev("Peak fall color", "fall_color",
           "Perhaps the finest fall color of any tree — blazing orange, red, and yellow simultaneously",
           "10-01", "10-30"),
    ],
    "Maple-Freeman's": [
        ev("Early red fall color", "fall_color",
           "Vivid red to orange-red color comes early, before most maples",
           "09-20", "10-15"),
    ],
    "Maple-Norway": [
        ev("Yellow-green spring flowers", "bloom",
           "Chartreuse-yellow flower clusters appear with the leaves — quite showy up close",
           "04-10", "05-01"),
        ev("Yellow fall color", "fall_color",
           "Clear yellow fall color",
           "10-10", "11-05"),
    ],
    "Maple-Japanese": [
        ev("Crimson fall color", "fall_color",
           "Delicate leaves turn an electric crimson-red — among the finest fall color of any tree",
           "10-15", "11-05"),
        ev("Spring red leafing", "foliage",
           "Red-leaved cultivars emerge in deep burgundy-red in spring",
           "04-10", "04-30"),
    ],
    "Maple-Amur": [
        ev("Red fall color", "fall_color",
           "Rich red fall color — one of the earliest maples to color up",
           "09-25", "10-20"),
        ev("Red winged fruits", "fruit",
           "Showy red-winged samaras are ornamental in late summer",
           "07-15", "09-15"),
    ],
    "Maple-Paperbark": [
        ev("Cinnamon peeling bark", "bark",
           "Cinnamon-orange papery bark peels in curling sheets year-round — stunning in winter light",
           "01-01", "12-31"),
        ev("Red-orange fall color", "fall_color",
           "Leaves turn orange-red, pairing beautifully with the cinnamon bark",
           "10-10", "11-01"),
    ],
    "Maple-Three Flower": [
        ev("Exfoliating bark", "bark",
           "Shaggy gray-brown bark exfoliates to reveal inner layers — best in winter",
           "11-15", "03-31"),
        ev("Orange-red fall color", "fall_color",
           "Bold orange and red fall color",
           "10-01", "10-25"),
    ],
    "Maple-David's": [
        ev("Striped green bark", "bark",
           "Distinctive green bark with white vertical stripes — one of the 'snakebark' maples",
           "01-01", "12-31"),
        ev("Yellow-orange fall color", "fall_color",
           "Bright yellow to orange fall color contrasting with the striped bark",
           "10-05", "10-30"),
    ],
    "Maple-Shantung": [
        ev("Orange-red fall color", "fall_color",
           "Rich orange to red fall color",
           "10-01", "10-25"),
    ],
    "Maple-Trident": [
        ev("Orange-red fall color", "fall_color",
           "Reliable orange to red fall color",
           "10-10", "11-05"),
    ],
    "Maple-Hedge": [
        ev("Yellow fall color", "fall_color",
           "Clear yellow fall color",
           "10-10", "11-05"),
    ],
    "Maple-Silver": [
        ev("Early red flowers", "bloom",
           "Small red flowers appear very early on bare branches",
           "03-10", "04-01"),
        ev("Yellow fall color", "fall_color",
           "Pale yellow fall color; silver leaf undersides flash in the wind all season",
           "10-10", "11-01"),
    ],
    "Maple-Boxelder": [
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-05", "10-25"),
    ],
    "Maple-Ivyleaved": [
        ev("Fall color", "fall_color",
           "Yellow-orange fall color on unusual ivy-shaped leaves",
           "10-10", "10-30"),
    ],
    "Maple-Sycamore": [
        ev("Yellow fall color", "fall_color",
           "Yellow fall color on large maple leaves",
           "10-15", "11-05"),
    ],

    # ── BIRCHES ───────────────────────────────────────────────────────────────
    "Birch-River": [
        ev("Exfoliating salmon bark", "bark",
           "Creamy salmon-to-tan papery bark peels in curling sheets year-round — beautiful in winter",
           "01-01", "12-31"),
        ev("Yellow fall color", "fall_color",
           "Bright yellow fall color with the peeling bark making a striking combination",
           "10-10", "10-30"),
    ],
    "Birch-Paper": [
        ev("Bright white bark", "bark",
           "Gleaming white papery bark stands out year-round, especially dramatic in winter and against fall color",
           "01-01", "12-31"),
        ev("Yellow fall color", "fall_color",
           "Warm golden-yellow fall color set against the white bark",
           "10-10", "10-30"),
    ],
    "Birch-Gray": [
        ev("Yellow fall color", "fall_color",
           "Golden yellow fall color",
           "10-10", "10-30"),
    ],

    # ── TULIPTREE (NPN NY bloom ~May 23, fall ~Oct 16) ───────────────────────
    "Tuliptree": [
        ev("Tulip-shaped flowers", "bloom",
           "Uniquely tulip-shaped flowers — green, orange, and yellow — appear in the canopy",
           "05-15", "06-10"),
        ev("Golden fall color", "fall_color",
           "Bright golden-yellow fall color lights up the canopy",
           "10-10", "10-30"),
        ev("Persistent cone-like fruits", "fruit",
           "Cone-like fruiting clusters stand upright on branches through winter",
           "10-01", "02-15"),
    ],

    # ── SWEETGUM (NPN NY fall ~Oct 28) ──────────────────────────────────────
    "Sweetgum-Common": [
        ev("Multicolor fall color", "fall_color",
           "Spectacular star-shaped leaves turn wine, purple, orange, red, and yellow — often all on the same tree",
           "10-10", "11-10"),
        ev("Spiky ball fruits", "fruit",
           "Spiky round ball fruits hang through winter",
           "10-15", "02-15"),
    ],

    # ── TUPELO-BLACK (NPN NY fall ~Oct 18 — first to turn!) ──────────────────
    "Tupelo-Black": [
        ev("First fall color — scarlet", "fall_color",
           "One of the FIRST trees on campus to color up — brilliant scarlet red, sometimes as early as mid-September",
           "09-20", "10-20"),
    ],

    # ── GINKGO ────────────────────────────────────────────────────────────────
    "Ginkgo": [
        ev("Golden fall color", "fall_color",
           "Leaves turn a pure luminous gold, then drop all at once within days — the golden carpet is spectacular",
           "10-15", "11-01"),
        ev("Fan-shaped spring leaves", "foliage",
           "Prehistoric fan-shaped leaves unfurl in pale green",
           "04-15", "05-10"),
    ],

    # ── DAWN REDWOOD ──────────────────────────────────────────────────────────
    "Dawn Redwood": [
        ev("Fresh green needle emergence", "foliage",
           "Vivid bright-green feathery needles burst from bare branches — one of the most dramatic spring emergences",
           "04-15", "05-10"),
        ev("Copper-orange fall color", "fall_color",
           "Soft needles turn a rich copper-orange before the tree goes bare — striking contrast with the large trunk",
           "10-25", "11-15"),
    ],

    # ── LARCHES ──────────────────────────────────────────────────────────────
    "Larch-Common": [
        ev("Bright green spring needles", "foliage",
           "Soft bright-green needles emerge early — one of the first conifers to leaf out in spring",
           "03-20", "04-25"),
        ev("Golden fall color", "fall_color",
           "Needles turn golden-yellow before dropping — unusual for a conifer",
           "10-15", "11-10"),
    ],
    "Larch": [
        ev("Spring needle emergence", "foliage",
           "Soft green needles emerge on a deciduous conifer",
           "03-20", "04-25"),
        ev("Golden fall color", "fall_color",
           "Needles turn golden yellow",
           "10-15", "11-05"),
    ],
    "Golden Larch": [
        ev("Soft spring needles", "foliage",
           "Soft golden-green needles emerge on this beautiful rare deciduous conifer",
           "04-01", "05-01"),
        ev("Brilliant golden fall color", "fall_color",
           "Needles turn brilliant pure gold — one of the finest autumn displays of any conifer",
           "10-15", "11-10"),
    ],

    # ── COMMON BALDCYPRESS ───────────────────────────────────────────────────
    "Common Baldcypress": [
        ev("Fresh green spring needles", "foliage",
           "Feathery bright-green needles emerge on this unusual deciduous conifer",
           "04-10", "05-05"),
        ev("Russet-copper fall color", "fall_color",
           "Needles turn soft russet to burnt copper before dropping",
           "10-20", "11-15"),
    ],

    # ── KATSURATREE ──────────────────────────────────────────────────────────
    "Katsuratree": [
        ev("Rosy spring leaf emergence", "foliage",
           "Heart-shaped leaves emerge with a rosy-red flush before turning blue-green",
           "04-05", "05-05"),
        ev("Caramel-scented fall color", "fragrance",
           "UNIQUE: Fallen leaves release a warm caramel / burnt-sugar fragrance — the sweetest smell in the arboretum",
           "10-01", "10-30"),
        ev("Yellow-orange fall color", "fall_color",
           "Leaves turn warm yellow to apricot-orange",
           "10-01", "10-30"),
    ],

    # ── YELLOWWOOD ────────────────────────────────────────────────────────────
    "Yellowwood-American": [
        ev("Fragrant white flower racemes", "bloom",
           "Long hanging clusters of fragrant white flowers — one of the most beautiful and fragrant of all flowering trees",
           "05-20", "06-10"),
        ev("Smooth gray bark", "bark",
           "Smooth light-gray bark resembles beech — beautiful in winter",
           "11-15", "03-31"),
        ev("Yellow fall color", "fall_color",
           "Clear yellow fall color",
           "10-01", "10-25"),
    ],

    # ── LOCUST-BLACK (NPN NY bloom ~May 9) ───────────────────────────────────
    "Locust-Black": [
        ev("Fragrant white bloom", "bloom",
           "Hanging clusters of fragrant white flowers — the whole area around these trees smells of honey",
           "05-05", "05-25"),
        ev("Yellow fall color", "fall_color",
           "Small leaflets turn yellow",
           "10-05", "10-20"),
    ],

    # ── REDBUD FAMILY / HONEYLOCUST ──────────────────────────────────────────
    "Honeylocust-Thornless Common": [
        ev("Yellow fall color", "fall_color",
           "Small leaflets turn a bright clean yellow, creating a fine-textured golden canopy",
           "10-10", "11-05"),
    ],

    # ── HORSECHESTNUT ─────────────────────────────────────────────────────────
    "Horsechestnut-Red": [
        ev("Red flower candles", "bloom",
           "Upright candles of showy red-pink flowers tower above the foliage",
           "04-25", "05-20"),
    ],

    # ── SILVERBELL ────────────────────────────────────────────────────────────
    "Silverbell-Carolina": [
        ev("White bell flowers", "bloom",
           "Chains of dainty white bell-shaped flowers dangle beneath the branches",
           "04-20", "05-10"),
        ev("Yellow fall color", "fall_color",
           "Clean yellow fall color",
           "10-10", "10-30"),
    ],

    # ── STYRAX ────────────────────────────────────────────────────────────────
    "Styrax-Japanese Snowbell": [
        ev("Fragrant white bells", "bloom",
           "Masses of drooping white bell-shaped fragrant flowers — stunning when viewed from below",
           "05-25", "06-20"),
    ],
    "Styrax-Snowbell": [
        ev("Fragrant white bells", "bloom",
           "Drooping white fragrant bell-shaped flowers",
           "05-25", "06-20"),
    ],

    # ── LINDENS (fragrant!) ────────────────────────────────────────────────────
    "Linden": [
        ev("Intensely fragrant bloom", "fragrance",
           "Small cream-yellow flowers produce one of the most powerfully sweet fragrances in the arboretum — bees swarm these trees",
           "06-20", "07-15"),
    ],
    "Linden-Littleleaf": [
        ev("Intensely fragrant bloom", "fragrance",
           "Small cream flowers fill the air with a uniquely sweet honey-like fragrance",
           "06-25", "07-20"),
    ],
    "Linden-American": [
        ev("Fragrant summer bloom", "fragrance",
           "Hanging clusters of cream-yellow fragrant flowers",
           "06-20", "07-15"),
    ],
    "Linden-Silver": [
        ev("Fragrant bloom", "fragrance",
           "Cream flowers with a distinctive lime-blossom fragrance",
           "06-25", "07-20"),
    ],

    # ── SMOKETREE ─────────────────────────────────────────────────────────────
    "Cotinus-Common Smoketree": [
        ev("Smoky puffball display", "bloom",
           "Wispy pink-purple flower plumes create a smoke-like haze around the tree — unique",
           "06-01", "07-15"),
        ev("Red-orange fall color", "fall_color",
           "Leaves turn vivid orange, red, and burgundy",
           "10-01", "10-20"),
    ],

    # ── MIMOSA / ALBIZIA ──────────────────────────────────────────────────────
    "Mimosa": [
        ev("Pink powderpuff flowers", "bloom",
           "Fluffy pink powderpuff flowers create an exotic tropical display",
           "06-25", "08-01"),
    ],

    # ── PAGODATREE ────────────────────────────────────────────────────────────
    "Pagodatree-Japanese": [
        ev("Late white bloom", "bloom",
           "Upright clusters of white pea-like flowers in late summer — one of the last trees to bloom",
           "07-15", "08-10"),
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-05", "10-25"),
    ],

    # ── SEVEN-SON FLOWER ─────────────────────────────────────────────────────
    "Seven-son Flower": [
        ev("Late summer bloom + bracts", "bloom",
           "White flowers followed by showy rose-red sepals that look like flowers — blooms and 'blooms twice'",
           "08-20", "10-01"),
    ],

    # ── STEWARTIAS ────────────────────────────────────────────────────────────
    "Stewartia-Japanese": [
        ev("Camellia-like flowers", "bloom",
           "Large white camellia-like flowers with orange-yellow stamens — outstanding summer bloomer",
           "06-20", "08-01"),
        ev("Exfoliating mosaic bark", "bark",
           "Bark exfoliates in a mosaic of cream, gray, brown, and rust — one of the finest bark trees year-round",
           "01-01", "12-31"),
        ev("Red-purple fall color", "fall_color",
           "Leaves turn red to purple-red",
           "10-10", "11-01"),
    ],
    "Stewartia": [
        ev("White flowers", "bloom",
           "White camellia-like flowers in summer",
           "06-20", "08-01"),
        ev("Exfoliating bark", "bark",
           "Attractive exfoliating bark reveals mosaic of colors",
           "01-01", "12-31"),
    ],

    # ── ENKIANTHUS ────────────────────────────────────────────────────────────
    "Enkianthus": [
        ev("Pink bell flowers", "bloom",
           "Pendulous clusters of creamy-pink striped bell-shaped flowers",
           "05-01", "05-25"),
        ev("Brilliant fall color", "fall_color",
           "One of the finest fall colors of any shrub/small tree — scarlet to orange to yellow",
           "10-05", "10-30"),
    ],

    # ── MAACKIA ───────────────────────────────────────────────────────────────
    "Maackia-Amur": [
        ev("White midsummer bloom", "bloom",
           "Upright white flower racemes in midsummer",
           "07-01", "08-01"),
        ev("Peeling copper-bronze bark", "bark",
           "Bark peels in thin copper-bronze flakes — handsome year-round",
           "01-01", "12-31"),
    ],

    # ── HARDY RUBBER TREE ─────────────────────────────────────────────────────
    "Hardy Rubber Tree": [
        ev("Yellow fall color", "fall_color",
           "Clear yellow fall color on this unusual novelty tree",
           "10-10", "11-01"),
    ],

    # ── ELMS ──────────────────────────────────────────────────────────────────
    "Elm-American": [
        ev("Yellow fall color", "fall_color",
           "Clear yellow fall color on the classic vase-shaped American Elm",
           "10-15", "11-05"),
    ],
    "Elm-Chinese": [
        ev("Mottled exfoliating bark", "bark",
           "Bark exfoliates in irregular patches of gray, green, orange, and brown — beautiful year-round",
           "01-01", "12-31"),
        ev("Yellow-green fall color", "fall_color",
           "Late-season yellow to yellow-green fall color",
           "10-20", "11-10"),
    ],
    "Elm-Siberian": [
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-10", "11-01"),
    ],
    "Elm-Slippery": [
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-10", "11-01"),
    ],
    "Elm-Smooth Leaved": [
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-10", "11-01"),
    ],

    # ── ZELKOVA ───────────────────────────────────────────────────────────────
    "Zelkova-Japanese": [
        ev("Orange-red fall color", "fall_color",
           "Leaves turn yellow, orange, and red — a vase-shaped tree with excellent fall color",
           "10-15", "11-05"),
    ],

    # ── BEECH ─────────────────────────────────────────────────────────────────
    "Beech-American": [
        ev("Silky spring leaf emergence", "foliage",
           "Pale green silky leaves unfurl from long pointed buds — one of the most beautiful leaf emergences of any tree",
           "04-20", "05-15"),
        ev("Smooth silver bark", "bark",
           "Smooth silver-gray bark is strikingly beautiful, especially in winter",
           "11-15", "04-01"),
        ev("Bronze-gold fall color", "fall_color",
           "Leaves turn bronze-gold and many persist through winter on the tree",
           "10-20", "11-15"),
    ],
    "Beech-European": [
        ev("Silky spring leaf emergence", "foliage",
           "Silky pale green leaves emerge from long winter buds",
           "04-20", "05-10"),
        ev("Smooth gray bark", "bark",
           "Smooth elephant-skin gray bark is beautiful year-round",
           "11-15", "04-01"),
        ev("Copper-bronze fall color", "fall_color",
           "Copper to bronze fall color; purple-leaved varieties turn dark bronze",
           "10-20", "11-10"),
    ],

    # ── OAKS ─────────────────────────────────────────────────────────────────
    "Oak-Scarlet": [
        ev("Brilliant scarlet fall color", "fall_color",
           "One of the finest fall colors of any oak — brilliant scarlet red that rivals the maples",
           "10-15", "11-10"),
    ],
    "Oak-Pin": [
        ev("Red-brown fall color", "fall_color",
           "Leaves turn russet-red to red-brown; many persist on the tree into winter",
           "10-20", "11-15"),
    ],
    "Oak-Northern Red": [
        ev("Red to orange-brown fall color", "fall_color",
           "Reliable red to orange-brown fall color on one of campus's most common trees",
           "10-15", "11-10"),
    ],
    "Oak-White": [
        ev("Burgundy-red fall color", "fall_color",
           "Rich burgundy to wine-red fall color on the stately white oak",
           "10-20", "11-10"),
    ],
    "Oak-Swamp White": [
        ev("Yellow-brown fall color", "fall_color",
           "Yellow to yellow-brown fall color with attractive exfoliating bark",
           "10-15", "11-05"),
        ev("Exfoliating bark", "bark",
           "Bark on upper branches peels in curling strips, revealing lighter inner bark",
           "01-01", "12-31"),
    ],
    "Oak-English": [
        ev("Yellow-brown fall color", "fall_color",
           "Yellow-brown fall color",
           "10-15", "11-10"),
    ],
    "Oak-Bur": [
        ev("Yellow fall color", "fall_color",
           "Yellow fall color on massive fringed-cap acorns tree",
           "10-20", "11-10"),
    ],
    "Oak-Black": [
        ev("Red-brown fall color", "fall_color",
           "Red to red-brown fall color",
           "10-20", "11-10"),
    ],
    "Oak-Sawtooth": [
        ev("Yellow fall color", "fall_color",
           "Yellow to yellow-brown fall color",
           "10-15", "11-05"),
    ],
    "Oak-Willow": [
        ev("Yellow fall color", "fall_color",
           "Yellow to yellow-brown fall color on willow-like narrow leaves",
           "10-20", "11-10"),
    ],
    "Oak-Chestnut": [
        ev("Yellow-brown fall color", "fall_color",
           "Yellow to yellow-brown fall color",
           "10-20", "11-10"),
    ],
    "Oak-Chinkapin": [
        ev("Yellow-orange fall color", "fall_color",
           "Orange to yellow-orange fall color",
           "10-15", "11-05"),
    ],
    "Oak-Shingle": [
        ev("Yellow-red fall color", "fall_color",
           "Yellow to red fall color",
           "10-20", "11-05"),
    ],
    "Oak": [
        ev("Fall color", "fall_color",
           "Red to brown fall color",
           "10-20", "11-10"),
    ],

    # ── SASSAFRAS ─────────────────────────────────────────────────────────────
    "Sassafras-Common": [
        ev("Multicolor fall display", "fall_color",
           "Leaves on one tree can turn orange, red, purple, AND yellow simultaneously — outstanding multicolor fall display",
           "10-01", "10-25"),
        ev("Aromatic leaves", "fragrance",
           "Mitten-shaped leaves release a spicy root-beer scent when crushed",
           "05-01", "10-31"),
    ],

    # ── PERSIMMON ─────────────────────────────────────────────────────────────
    "Persimmon-Common": [
        ev("Orange fruits persist", "fruit",
           "Orange fruits cling to bare branches after leaf drop — beautiful against the winter sky",
           "10-15", "12-15"),
        ev("Yellow fall color", "fall_color",
           "Leaves turn yellow to orange-yellow",
           "10-15", "11-05"),
    ],

    # ── TUPELO ── already done above ─────────────────────────────────────────

    # ── POPLAR / ASPEN ────────────────────────────────────────────────────────
    "Poplar-Aspen": [
        ev("Golden trembling fall color", "fall_color",
           "Golden yellow leaves tremble and flutter in any breeze — the whispering sound is as beautiful as the color",
           "10-05", "10-25"),
    ],
    "Poplar-Eastern": [
        ev("Golden fall color", "fall_color",
           "Golden yellow fall color",
           "10-10", "10-30"),
    ],

    # ── PLANETREE / SYCAMORE ──────────────────────────────────────────────────
    "Planetree-London": [
        ev("Camouflage exfoliating bark", "bark",
           "Bark peels in large patches to reveal cream, olive, and tan — creating a dramatic camouflage pattern year-round",
           "01-01", "12-31"),
        ev("Yellow-brown fall color", "fall_color",
           "Yellow to yellow-brown fall color",
           "10-20", "11-10"),
    ],
    "Sycamore-American": [
        ev("Camouflage bark", "bark",
           "Upper branches show striking white-cream bark from exfoliation — ghostly white in winter",
           "01-01", "12-31"),
        ev("Yellow-brown fall color", "fall_color",
           "Yellow to yellow-brown fall color",
           "10-20", "11-10"),
    ],

    # ── HICKORIES ─────────────────────────────────────────────────────────────
    "Hickory-Shagbark": [
        ev("Shaggy bark display", "bark",
           "Long curling gray bark plates give the tree its distinctive shaggy look — dramatic year-round",
           "01-01", "12-31"),
        ev("Golden fall color", "fall_color",
           "Rich golden yellow fall color — among the finest yellows of any native tree",
           "10-10", "11-01"),
    ],
    "Hickory-Pignut": [
        ev("Golden fall color", "fall_color",
           "Warm golden yellow fall color",
           "10-10", "11-01"),
    ],

    # ── WALNUT ────────────────────────────────────────────────────────────────
    "Walnut-Black": [
        ev("Early yellow fall color", "fall_color",
           "Leaflets turn yellow and drop early — one of the first trees to go bare in fall",
           "10-01", "10-20"),
    ],

    # ── HORNBEAMS ─────────────────────────────────────────────────────────────
    "Hornbeam-American": [
        ev("Muscular fluted bark", "bark",
           "Smooth gray bark is deeply fluted into muscle-like ridges — striking in winter",
           "11-15", "03-31"),
        ev("Orange-red fall color", "fall_color",
           "Orange-red fall color",
           "10-10", "11-01"),
        ev("Hop-like fruits", "fruit",
           "Hanging clusters of leafy hop-like fruits are ornamental",
           "09-01", "11-01"),
    ],
    "Hornbeam-European": [
        ev("Muscular gray bark", "bark",
           "Smooth gray muscular-looking bark is ornamental year-round",
           "11-15", "03-31"),
        ev("Yellow-orange fall color", "fall_color",
           "Yellow to orange fall color, leaves may persist",
           "10-10", "11-05"),
    ],

    # ── HACKBERRY ─────────────────────────────────────────────────────────────
    "Hackberry": [
        ev("Corky warty bark", "bark",
           "Distinctively warty and corky bark with irregular ridges — very recognizable",
           "01-01", "12-31"),
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-15", "11-05"),
        ev("Purple berries attract birds", "fruit",
           "Small purple-black berries attract dozens of bird species during fall migration",
           "09-01", "11-01"),
    ],

    # ── HAZEL / FILBERT ───────────────────────────────────────────────────────
    "Hazel-Turkish Filbert": [
        ev("Yellow fall color", "fall_color",
           "Clear yellow fall color",
           "10-05", "10-30"),
    ],

    # ── HOLLIES ───────────────────────────────────────────────────────────────
    "Holly-American": [
        ev("Red berries on evergreen", "fruit",
           "Brilliant red berries against glossy dark evergreen foliage — at its best in late fall and winter",
           "10-15", "02-15"),
    ],
    "Holly-English": [
        ev("Red berries on evergreen", "fruit",
           "Classic Christmas-red berries against dark spiny evergreen leaves",
           "10-15", "02-15"),
    ],

    # ── MOUNTAIN ASH ──────────────────────────────────────────────────────────
    "Mountain Ash-Korean": [
        ev("White bloom clusters", "bloom",
           "Flat-topped clusters of small white flowers",
           "05-01", "05-25"),
        ev("Brilliant orange-red fruits", "fruit",
           "Large clusters of bright orange-red fruits are stunning and very bird-attractive",
           "09-01", "11-15"),
        ev("Orange-red fall color", "fall_color",
           "Orange-red fall color",
           "10-01", "10-25"),
    ],

    # ── OSAGE ORANGE ─────────────────────────────────────────────────────────
    "Osage Orange": [
        ev("Giant wrinkled fruits", "fruit",
           "Grapefruit-sized bumpy green fruits litter the ground in fall — nature's most remarkable fruit",
           "09-15", "12-01"),
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-10", "11-01"),
    ],

    # ── MULBERRY ─────────────────────────────────────────────────────────────
    "Mulberry-White": [
        ev("Sweet berries", "fruit",
           "Sweet white to pale-pink mulberries ripen — edible, and irresistible to birds",
           "06-01", "07-15"),
    ],

    # ── PAWPAW ────────────────────────────────────────────────────────────────
    "Pawpaw-Common": [
        ev("Large tropical-looking fruits", "fruit",
           "Large oblong green fruits — the largest edible fruit native to North America, with a banana-custard flavor",
           "09-01", "10-10"),
        ev("Yellow fall color", "fall_color",
           "Clear yellow fall color on large tropical-looking leaves",
           "10-01", "10-25"),
    ],

    # ── CORKTREE ─────────────────────────────────────────────────────────────
    "Corktree-Amur": [
        ev("Deeply ridged corky bark", "bark",
           "Thick corky deeply-furrowed bark is very distinctive year-round",
           "01-01", "12-31"),
        ev("Yellow fall color", "fall_color",
           "Yellow fall color",
           "10-05", "10-20"),
    ],

    # ── SASSAFRAS already done ───────────────────────────────────────────────

    # ── KENTUCKY COFFEETREE ───────────────────────────────────────────────────
    "Kentucky Coffeetree": [
        ev("Bold winter silhouette", "bark",
           "Stout contorted branches with rough scaly bark create a dramatic winter silhouette",
           "11-15", "03-31"),
        ev("Large brown pods persist", "fruit",
           "Large leathery brown seed pods hang through winter",
           "10-01", "02-15"),
        ev("Yellow fall color", "fall_color",
           "Yellow fall color on large bipinnate leaves",
           "10-05", "10-25"),
    ],

    # ── CHESTNUT ─────────────────────────────────────────────────────────────
    "Chestnut-Chinese": [
        ev("Spiny chestnut burrs", "fruit",
           "Spiny burrs open to reveal shiny brown chestnuts in early fall",
           "09-15", "10-20"),
        ev("Yellow fall color", "fall_color",
           "Yellow-brown fall color",
           "10-10", "11-01"),
    ],

    # ── LINDEN ALREADY DONE ──────────────────────────────────────────────────

    # ── TUPELO ALREADY DONE ──────────────────────────────────────────────────

    # ── SOPHORA / PAGODATREE ALREADY DONE ────────────────────────────────────

    # ── SERVICEBERRY ALREADY DONE ────────────────────────────────────────────

    # ── REDBUD ALREADY DONE ──────────────────────────────────────────────────

    # ── SWEETGUM ALREADY DONE ────────────────────────────────────────────────

    # ── BALDCYPRESS ALREADY DONE ─────────────────────────────────────────────

    # ── TREE OF HEAVEN ────────────────────────────────────────────────────────
    "Tree of Heaven": [
        ev("Showy seed clusters", "fruit",
           "Large clusters of winged seeds turn red-orange — ornamental despite the tree's weedy reputation",
           "08-15", "10-15"),
    ],

    # ── ELAEAGNUS / RUSSIAN OLIVE ─────────────────────────────────────────────
    "Elaeagnus-Russian Olive": [
        ev("Silver foliage all season", "foliage",
           "Silvery-gray foliage shimmers in the breeze all summer — unique color among campus trees",
           "05-01", "10-15"),
        ev("Fragrant summer bloom", "fragrance",
           "Tiny silver flowers produce a powerfully sweet vanilla-like fragrance",
           "06-01", "07-01"),
    ],

    # ── TULIPTREE ALREADY DONE ───────────────────────────────────────────────

    # ── PLANETREE ALREADY DONE ───────────────────────────────────────────────

    # ── CRYPTOMERIA ─────────────────────────────────────────────────────────
    "Japanese Cryptomeria": [
        ev("Bronze winter foliage", "foliage",
           "Foliage turns reddish-bronze in winter cold — returns to green in spring",
           "11-15", "03-15"),
    ],

    # ── SPRUCE / PINE / FIR / HEMLOCK — interest is year-round, skip unless notable ──
    # Most conifers don't have dramatic seasonal moments; skip unless special.

    # ── JAPANESE UMBRELLA PINE ────────────────────────────────────────────────
    "Japanese Umbrella Pine": [
        ev("Architectural form", "foliage",
           "Unusual whorled glossy green needles and perfect tiered form — a botanical curiosity year-round",
           "01-01", "12-31"),
    ],

    # ── LACEBARK PINE ─────────────────────────────────────────────────────────
    "Pine-Lacebark": [
        ev("Mosaic flaking bark", "bark",
           "Bark exfoliates in patches to reveal a mosaic of cream, green, gray, and brown — one of the most ornamental barks of any pine",
           "01-01", "12-31"),
    ],

    # ── FALSECYPRESS ─────────────────────────────────────────────────────────
    "Falsecypress-Hinoki": [
        ev("Fan-like foliage", "foliage",
           "Elegant fan-shaped dark-green fronds with white markings underneath — beautiful all year",
           "01-01", "12-31"),
    ],

    # ── WITCHHAZEL ALREADY DONE ──────────────────────────────────────────────

    # ── MIMOSA ALREADY DONE ──────────────────────────────────────────────────

    # ── ELM ALREADY DONE ─────────────────────────────────────────────────────

    # ── PLANE ALREADY DONE ───────────────────────────────────────────────────

    # ── ASH ──────────────────────────────────────────────────────────────────
    "Ash-Green": [
        ev("Purple fall color", "fall_color",
           "Leaves turn yellow to purple — unusual for an ash",
           "10-05", "10-30"),
    ],

    # ── WILLOW ───────────────────────────────────────────────────────────────
    "Willow": [
        ev("Early spring green", "foliage",
           "One of the first trees to leaf out in spring — a welcome sight",
           "03-20", "04-20"),
    ],

    # ── RUSSIANOLIVE ALREADY DONE ────────────────────────────────────────────

    # ── GOLDENRAINTREE / KOELREUTERIA ─────────────────────────────────────────
    # Not in our species list, skip

    # ── EHRETIA ──────────────────────────────────────────────────────────────
    "Ehretia": [
        ev("White bloom clusters", "bloom",
           "Flat-topped clusters of small white fragrant flowers",
           "06-01", "07-01"),
    ],

    # ── VIBURNUM ─────────────────────────────────────────────────────────────
    "Viburnum": [
        ev("White flower clusters", "bloom",
           "Flat or domed clusters of white flowers",
           "05-01", "05-25"),
        ev("Colorful fruits", "fruit",
           "Berries change from green to yellow to red to blue-black — multiple colors at once",
           "08-15", "10-15"),
    ],

    # ── ALDER ─────────────────────────────────────────────────────────────────
    "Alder-Speckled": [
        ev("Early catkins", "bloom",
           "Dangling yellow-brown catkins open before leaves in very early spring",
           "03-01", "04-01"),
        ev("Yellow fall color", "fall_color",
           "Yellow to yellow-green fall color",
           "10-10", "10-30"),
    ],

    # ── SYMPLOCOS / ASIATIC SWEETLEAF ─────────────────────────────────────────
    "Asiatic Sweetleaf": [
        ev("White bloom clusters", "bloom",
           "Dense clusters of small white fragrant flowers",
           "05-01", "05-25"),
        ev("Brilliant blue fruits", "fruit",
           "Turquoise-blue fruits are among the most unusually colored fruits of any hardy tree",
           "09-01", "10-15"),
    ],

    # ── CEDAR ATLAS / DEODAR ──────────────────────────────────────────────────
    "Cedar-Atlas": [
        ev("Blue-gray foliage", "foliage",
           "Blue-gray foliage is striking year-round, especially the blue-needled forms",
           "01-01", "12-31"),
    ],
    "Cedar-Deodar": [
        ev("Graceful weeping form", "foliage",
           "Elegant drooping branch tips and soft blue-green foliage create a graceful silhouette year-round",
           "01-01", "12-31"),
    ],

    # ── CONIFERS WITH NOTABLE MOMENTS ─────────────────────────────────────────
    "Pine-Eastern White": [
        ev("Spring candles", "foliage",
           "New growth 'candles' of bright soft green emerge in late spring — fresh and vivid before hardening",
           "05-01", "06-01"),
    ],
    "Spruce-Norway": [
        ev("Hanging cones", "fruit",
           "Long pendant cones up to 6\" hang like Christmas ornaments from the branch tips in fall",
           "09-15", "12-01"),
    ],
    "Spruce-Colorado Blue": [
        ev("Intense blue foliage", "foliage",
           "The most striking blue foliage of any conifer — the steel-blue color is vivid year-round",
           "01-01", "12-31"),
    ],
    "Hemlock-Canadian": [
        ev("Elegant drooping tips", "foliage",
           "Graceful nodding branch tips with fine dark-green foliage create a soft elegant form year-round",
           "01-01", "12-31"),
    ],
    "Juniper-Eastern Redcedar": [
        ev("Blue-gray berries", "fruit",
           "Blue-gray waxy berry-like cones ripen in fall — a critical food for Cedar Waxwings during migration",
           "09-15", "12-15"),
    ],
    "Yew-English": [
        ev("Scarlet berries (toxic)", "fruit",
           "Bright scarlet fleshy berries contrast dramatically against dark evergreen foliage — NOTE: toxic to humans",
           "08-15", "11-15"),
    ],
    "Yew-Japanese": [
        ev("Scarlet berries (toxic)", "fruit",
           "Bright red fleshy berries on dark evergreen foliage — NOTE: toxic to humans",
           "08-15", "11-15"),
    ],
    "Douglas Fir": [
        ev("Spring candles", "foliage",
           "New growth emerges as vivid bright-green soft tufts at branch tips",
           "04-20", "05-25"),
    ],
    "Fir-White": [
        ev("Blue-green new growth", "foliage",
           "Fresh blue-green new growth brightens the tips of every branch in spring",
           "04-20", "05-25"),
    ],
    "Fir-Balsam": [
        ev("Upright purple cones", "fruit",
           "Upright purple-blue cones stand like candles on the upper branches in summer",
           "06-15", "09-15"),
    ],
    "Fir-Fraser": [
        ev("Upright cones", "fruit",
           "Distinctive upright cones with protruding bracts stand on the upper branches",
           "06-15", "09-15"),
    ],
    "Pine-Scotch": [
        ev("Orange-red bark on upper trunk", "bark",
           "Upper trunk and large branches display distinctive orange-red plated bark — beautiful year-round",
           "01-01", "12-31"),
    ],
    "Pine-Japanese White": [
        ev("Architectural form", "foliage",
           "Blue-green needles in distinctive bundles of 5 and elegant tiered form create a refined appearance year-round",
           "01-01", "12-31"),
    ],
    "Falsecypress-Sawara Cypress": [
        ev("Fine textured foliage", "foliage",
           "Soft feathery green or gold foliage creates a delicate texture year-round",
           "01-01", "12-31"),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# BUILD OUTPUT
# ─────────────────────────────────────────────────────────────────────────────
import csv, json as _json

def main():
    # Load sci name mapping
    enriched = _json.load(open('vassar_enriched.json'))
    sci_map = {}
    with open('vassar_arboretum.csv') as f:
        for row in csv.DictReader(f):
            name = row['common_name']
            bid = row['bartlett_id']
            sci = enriched.get(bid, {}).get('sci', '')
            if name not in sci_map and sci:
                sci_map[name] = sci

    out = {}
    covered = 0
    for name, events in SEASONAL.items():
        if events:
            out[name] = {
                "sci": sci_map.get(name, ""),
                "events": events,
            }
            covered += 1

    # Report species without seasonal data
    with open('vassar_arboretum.csv') as f:
        all_names = sorted(set(row['common_name'] for row in csv.DictReader(f)))

    print(f"\nCovered {covered} species with events")
    missing = [n for n in all_names if n not in SEASONAL]
    if missing:
        print(f"No events for {len(missing)} species (mostly conifers/generic):")
        for m in missing:
            print(f"  {m}")

    with open('vassar_seasonal.json', 'w') as f:
        _json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote vassar_seasonal.json ({len(out)} species)")

if __name__ == '__main__':
    main()

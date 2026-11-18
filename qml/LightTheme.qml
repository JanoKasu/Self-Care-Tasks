pragma Singleton

import QtQuick

QtObject {
    // Palette
    readonly property color canvas: "#F7F4FB"
    readonly property color canvasAlt: "#F2EFF8"
    readonly property color surface: "#FFFFFF"
    readonly property color divider: "#EEEAF3"

    readonly property color textPrimary: "#493D5C"
    readonly property color textSecondary: "#756A83"
    readonly property color textMuted: "#776D82"
    readonly property color accent: "#6F5B92"
    readonly property color accentLight: "#A98BD4"

    readonly property color landingStart: "#7357B7"
    readonly property color landingMiddle: "#A66DC4"
    readonly property color landingEnd: "#FF9F87"
    readonly property color landingGold: "#FFD79A"
    readonly property color landingMint: "#79DCC1"
    readonly property color landingCream: "#FFF2C7"
    readonly property color landingWhite: "#FFFFFF"
    readonly property color landingSoftWhite: "#FFF9FF"

    readonly property color morning: "#FFE2A9"
    readonly property color midday: "#CDE9DC"
    readonly property color evening: "#D9C9F1"
    readonly property color reflection: "#F7C9D1"
    readonly property color taskPeach: "#FBE3D5"
    readonly property color accentPeach: "#C47C58"
    readonly property color taskMint: "#DCEFE5"
    readonly property color impactHighGradientStart: "#FBE3E8"
    readonly property color impactHighGradientEnd: "#F5C9D3"
    readonly property color impactMediumGradientStart: "#DFF0E8"
    readonly property color impactMediumGradientEnd: "#C8E4D6"
    readonly property color impactLowGradientStart: "#FFF3D9"
    readonly property color impactLowGradientEnd: "#F4E0A9"
    readonly property color impactHigh: "#B84E65"
    readonly property color impactMedium: "#477A60"
    readonly property color impactLow: "#92743A"
    readonly property color impactHighSurface: "#F9DCE3"
    readonly property color impactLowSurface: "#F9EDC9"
    readonly property color checkboxBorder: "#B7A9C7"
    readonly property color progressTrack: "#EEE8F3"

    // Radii
    readonly property int radiusSmall: 10
    readonly property int radiusMedium: 16
    readonly property int radiusLarge: 22
    readonly property int radiusXLarge: 30

    // Spacing
    readonly property int spaceSmall: 8
    readonly property int spaceMedium: 14
    readonly property int spaceLarge: 24

    // Typography
    readonly property int fontSmall: 13
    readonly property int fontBody: 14
    readonly property int fontTitle: 28
}

pragma Singleton

import QtQuick

QtObject {
    id: root

    signal themeChanged(bool darkMode)

    property date currentTime: new Date()

    readonly property bool isDarkMode: isNightHour(currentTime.getHours())

    onIsDarkModeChanged: root.themeChanged(isDarkMode)

    function isNightHour(hour) {
        return hour >= 20 || hour < 6
    }

    function millisecondsUntilNextSwitch(time) {
        var nextSwitch = new Date(time.getTime())
        var hour = nextSwitch.getHours()

        if (hour < 6) {
            nextSwitch.setHours(6, 0, 0, 0)
        } else if (hour < 20) {
            nextSwitch.setHours(20, 0, 0, 0)
        } else {
            nextSwitch.setDate(nextSwitch.getDate() + 1)
            nextSwitch.setHours(6, 0, 0, 0)
        }

        return nextSwitch.getTime() - time.getTime()
    }

    property Timer refreshTimer: Timer {
        interval: root.millisecondsUntilNextSwitch(root.currentTime)
        repeat: false
        running: true
        onTriggered: {
            root.currentTime = new Date()
            root.refreshTimer.restart()
        }
    }

    readonly property color canvas: isDarkMode ? DarkTheme.canvas : LightTheme.canvas
    readonly property color canvasAlt: isDarkMode ? DarkTheme.canvasAlt : LightTheme.canvasAlt
    readonly property color surface: isDarkMode ? DarkTheme.surface : LightTheme.surface
    readonly property color divider: isDarkMode ? DarkTheme.divider : LightTheme.divider
    readonly property color textPrimary: isDarkMode ? DarkTheme.textPrimary : LightTheme.textPrimary
    readonly property color textSecondary: isDarkMode ? DarkTheme.textSecondary : LightTheme.textSecondary
    readonly property color textMuted: isDarkMode ? DarkTheme.textMuted : LightTheme.textMuted
    readonly property color accent: isDarkMode ? DarkTheme.accent : LightTheme.accent
    readonly property color accentLight: isDarkMode ? DarkTheme.accentLight : LightTheme.accentLight
    readonly property color landingStart: isDarkMode ? DarkTheme.landingStart : LightTheme.landingStart
    readonly property color landingMiddle: isDarkMode ? DarkTheme.landingMiddle : LightTheme.landingMiddle
    readonly property color landingEnd: isDarkMode ? DarkTheme.landingEnd : LightTheme.landingEnd
    readonly property color landingGold: isDarkMode ? DarkTheme.landingGold : LightTheme.landingGold
    readonly property color landingMint: isDarkMode ? DarkTheme.landingMint : LightTheme.landingMint
    readonly property color landingCream: isDarkMode ? DarkTheme.landingCream : LightTheme.landingCream
    readonly property color landingWhite: isDarkMode ? DarkTheme.landingWhite : LightTheme.landingWhite
    readonly property color landingSoftWhite: isDarkMode ? DarkTheme.landingSoftWhite : LightTheme.landingSoftWhite
    readonly property color morning: isDarkMode ? DarkTheme.morning : LightTheme.morning
    readonly property color midday: isDarkMode ? DarkTheme.midday : LightTheme.midday
    readonly property color evening: isDarkMode ? DarkTheme.evening : LightTheme.evening
    readonly property color reflection: isDarkMode ? DarkTheme.reflection : LightTheme.reflection
    readonly property color taskPeach: isDarkMode ? DarkTheme.taskPeach : LightTheme.taskPeach
    readonly property color accentPeach: isDarkMode ? DarkTheme.accentPeach : LightTheme.accentPeach
    readonly property color taskMint: isDarkMode ? DarkTheme.taskMint : LightTheme.taskMint
    readonly property color impactHighGradientStart: isDarkMode ? DarkTheme.impactHighGradientStart : LightTheme.impactHighGradientStart
    readonly property color impactHighGradientEnd: isDarkMode ? DarkTheme.impactHighGradientEnd : LightTheme.impactHighGradientEnd
    readonly property color impactMediumGradientStart: isDarkMode ? DarkTheme.impactMediumGradientStart : LightTheme.impactMediumGradientStart
    readonly property color impactMediumGradientEnd: isDarkMode ? DarkTheme.impactMediumGradientEnd : LightTheme.impactMediumGradientEnd
    readonly property color impactLowGradientStart: isDarkMode ? DarkTheme.impactLowGradientStart : LightTheme.impactLowGradientStart
    readonly property color impactLowGradientEnd: isDarkMode ? DarkTheme.impactLowGradientEnd : LightTheme.impactLowGradientEnd
    readonly property color impactHigh: isDarkMode ? DarkTheme.impactHigh : LightTheme.impactHigh
    readonly property color impactMedium: isDarkMode ? DarkTheme.impactMedium : LightTheme.impactMedium
    readonly property color impactLow: isDarkMode ? DarkTheme.impactLow : LightTheme.impactLow
    readonly property color impactHighSurface: isDarkMode ? DarkTheme.impactHighSurface : LightTheme.impactHighSurface
    readonly property color impactLowSurface: isDarkMode ? DarkTheme.impactLowSurface : LightTheme.impactLowSurface
    readonly property color checkboxBorder: isDarkMode ? DarkTheme.checkboxBorder : LightTheme.checkboxBorder
    readonly property color progressTrack: isDarkMode ? DarkTheme.progressTrack : LightTheme.progressTrack

    readonly property int radiusSmall: LightTheme.radiusSmall
    readonly property int radiusMedium: LightTheme.radiusMedium
    readonly property int radiusLarge: LightTheme.radiusLarge
    readonly property int radiusXLarge: LightTheme.radiusXLarge
    readonly property int spaceSmall: LightTheme.spaceSmall
    readonly property int spaceMedium: LightTheme.spaceMedium
    readonly property int spaceLarge: LightTheme.spaceLarge
    readonly property int fontSmall: LightTheme.fontSmall
    readonly property int fontBody: LightTheme.fontBody
    readonly property int fontTitle: LightTheme.fontTitle
}

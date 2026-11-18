import QtQuick
import QtQuick.Controls
import ".." as AppTheme

Button {
    id: root

    property bool primary: false

    implicitHeight: 52
    implicitWidth: 112
    hoverEnabled: true
    font.pixelSize: 15
    font.weight: Font.DemiBold

    background: Rectangle {
        radius: 16
        color: root.enabled
               ? (root.primary
                  ? (root.pressed ? Qt.darker(AppTheme.Theme.accent, 1.08)
                                 : AppTheme.Theme.accent)
                  : (root.pressed ? AppTheme.Theme.canvasAlt
                                 : AppTheme.Theme.canvas))
               : AppTheme.Theme.progressTrack
        border.width: root.primary ? 0 : 1
        border.color: root.primary ? "transparent" : AppTheme.Theme.divider

        Behavior on color {
            ColorAnimation { duration: 120 }
        }
    }

    contentItem: Text {
        text: root.text
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        color: root.enabled
               ? (root.primary ? AppTheme.Theme.surface
                              : AppTheme.Theme.textPrimary)
               : AppTheme.Theme.textMuted
        font: root.font
    }
}

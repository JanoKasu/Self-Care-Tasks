
import QtQuick
import ".." as AppTheme

Item {
    id: root

    // Public properties
    property bool checked: false
    property color checkedColor: AppTheme.Theme.accent
    property color uncheckedColor: AppTheme.Theme.surface
    property color borderColor: AppTheme.Theme.checkboxBorder
    property color checkColor: AppTheme.Theme.surface

    property int boxSize: 27
    property int cornerRadius: 9
    property string accessibleName: "Mark complete"

    signal toggled(bool checked)
    signal longPressed()

    implicitWidth: Math.max(boxSize, 56)
    implicitHeight: Math.max(boxSize, 56)
    activeFocusOnTab: true
    Accessible.role: Accessible.CheckBox
    Accessible.name: accessibleName
    Accessible.checked: checked

    Rectangle {
        id: box

        anchors.centerIn: parent

        width: root.boxSize
        height: root.boxSize

        radius: root.cornerRadius

        color: root.checked
               ? root.checkedColor
               : root.uncheckedColor

        scale: tapHandler.pressed ? 0.94 : 1
        border.width: 2
        border.color: root.checked
                      ? root.checkedColor
                      : root.borderColor

        Behavior on color {
            ColorAnimation { duration: 150 }
        }

        Behavior on border.color {
            ColorAnimation { duration: 150 }
        }

        Behavior on scale {
            NumberAnimation { duration: 90 }
        }

        Text {
            anchors.centerIn: parent

            text: "✓"
            color: root.checkColor

            font.pixelSize: root.boxSize * 0.65
            font.bold: true

            opacity: root.checked ? 1 : 0
            scale: root.checked ? 1 : 0.5

            Behavior on opacity {
                NumberAnimation { duration: 150 }
            }

            Behavior on scale {
                NumberAnimation { duration: 150 }
            }
        }
    }

    TapHandler {
        id: tapHandler
        property bool holdTriggered: false

        onTapped: {
            if (holdTriggered) {
                holdTriggered = false
                return
            }
            root.toggled(!root.checked)
        }
        onLongPressed: {
            holdTriggered = true
            root.longPressed()
        }
        onPressedChanged: {
            if (pressed)
                holdTriggered = false
        }
    }

    Keys.onPressed: function(event) {
        if (event.key === Qt.Key_Space || event.key === Qt.Key_Return
                || event.key === Qt.Key_Enter) {
            root.toggled(!root.checked)
            event.accepted = true
        }
    }
}

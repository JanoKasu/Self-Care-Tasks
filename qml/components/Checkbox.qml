
import QtQuick

Item {
    id: root

    // Public properties
    property bool checked: false
    property color checkedColor: "#75618F"
    property color uncheckedColor: "#FFFFFF"
    property color borderColor: "#B7A9C7"
    property color checkColor: "#FFFFFF"

    property int boxSize: 27
    property int cornerRadius: 9

    signal toggled(bool checked)

    implicitWidth: boxSize
    implicitHeight: boxSize

    Rectangle {
        id: box

        anchors.centerIn: parent

        width: root.boxSize
        height: root.boxSize

        radius: root.cornerRadius

        color: root.checked
               ? root.checkedColor
               : root.uncheckedColor

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
        onTapped: root.toggled(!root.checked)
    }
}

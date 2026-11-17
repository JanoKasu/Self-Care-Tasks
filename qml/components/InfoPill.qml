
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property string text: "2 hours"
    property string icon: ""
    property color accentColor: "#75618F"
    property color backgroundColor: "#E9DDF8"

    implicitWidth: content.implicitWidth + 24
    implicitHeight: 32

    radius: 16
    color: backgroundColor

    Row {
        id: content

        anchors.centerIn: parent
        spacing: 6

        Text {
            visible: root.icon !== ""
            text: root.icon
            color: root.accentColor
            font.pixelSize: 13
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.text
            color: root.accentColor
            font.pixelSize: 12
            font.weight: Font.DemiBold
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}


import QtQuick
import ".." as AppTheme

Rectangle {
    id: root

    property string text: "2 hours"
    property string icon: ""
    property color accentColor: AppTheme.Theme.accent
    property color backgroundColor: AppTheme.Theme.canvasAlt

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

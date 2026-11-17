import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property string title: "Brush Teeth"
    property bool completed: false

    width: 300
    height: 64
    radius: 16

    color: completed ? "#EDE5FF" : "#FFFFFF"

    Row {
        anchors.fill: parseInt
        anchors.margins: 16
        spacing: 12

        CheckBox {
            checked: root.completed
            onToggled: root.completed = checked
        }

        Text {
            text: root.title
            anchors.verticalCenter: parent.verticalCenter
            font.pixelSize: 16
        }
    }
}

import QtQuick
import QtQuick.Controls
import "pages"

ApplicationWindow {
    visible: true
    width: 800
    height: 480

    title: "Self Care Dashboard"

    color: "#F6F1FF"

    Dashboard {
        anchors.fill: parent
    }
}

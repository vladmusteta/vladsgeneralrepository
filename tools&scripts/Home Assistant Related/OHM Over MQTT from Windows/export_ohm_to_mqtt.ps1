# === CONFIG ===
$broker = "192.168.100.50"
$port = 31883
$topicRoot = "windows/ohm"
$ohmUrl = "http://localhost:8085/data.json"
$mosquitto = "C:\Program Files\mosquitto\mosquitto_pub.exe"

# === FETCH & PUBLISH ===
$data = Invoke-RestMethod -Uri $ohmUrl

function Publish-Sensors {
    param ($node, $path = "")
    if ($node.Text -and $node.Value -and $node.Value -match '\d') {
        $fullPath = "$path/$($node.Text)".Trim('/')
        $topic = $fullPath -replace '[^a-zA-Z0-9]+', '_'
        $value = ($node.Value -replace '[^\d\.\-]+', '')  # Clean value
        & $mosquitto -h $broker -p $port -t "$topicRoot/$topic" -m $value
    }
    foreach ($child in $node.Children) {
        Publish-Sensors -node $child -path "$path/$($node.Text)"
    }
}

Publish-Sensors -node $data

function VoiceConversationUI({ userId, onBack }) {
    const [messages, setMessages] = React.useState([]);
    const [typing, setTyping] = React.useState(false);
    const [recording, setRecording] = React.useState(false);

    const ws = React.useRef(null);
    const mediaRecorder = React.useRef(null);
    const botAudioChunks = React.useRef([]);
    const messagesEndRef = React.useRef(null);
    const botAudioRef = React.useRef(null); // Use ref, not getElementById

    React.useEffect(() => {
        var protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        console.log("protocol");
        console.log(protocol);
        ws.current = new WebSocket(`${protocol}://${location.host}/ws?user_id=${userId}`);
        ws.current.binaryType = "arraybuffer";

        ws.current.onopen = () => {
            console.log("WebSocket connection established");
        };

        ws.current.onmessage = async (event) => {
            if (typeof event.data === "string" && event.data.startsWith('{')) {
                const msg = JSON.parse(event.data);
                if (msg.type === "transcript") {
                    setMessages(prev => [
                        ...prev,
                        { message: msg.text, from: 'user' }
                    ]);
                }
                if (msg.type === "bot_text") {
                    setTyping(false);
                    setMessages(prev => [
                        ...prev,
                        { message: msg.text, from: 'bot' }
                    ]);
                }
            } else if (event.data instanceof ArrayBuffer) {
                const arr = new Uint8Array(event.data);
                if (arr.length === 9 && new TextDecoder().decode(arr) === "END_AUDIO") {
                    const audioBlob = new Blob(botAudioChunks.current, {type: 'audio/wav'});
                    if (botAudioRef.current) {
                        botAudioRef.current.src = URL.createObjectURL(audioBlob);
                        botAudioRef.current.play();
                    }
                    botAudioChunks.current = [];
                } else {
                    botAudioChunks.current.push(event.data);
                }
            }
        };

        ws.current.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        ws.current.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            ws.current && ws.current.close();
        };
    }, [userId]);

    React.useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const startRecording = async () => {
        setRecording(true);
        setTyping(true);
        botAudioChunks.current = [];
        let stream;
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (err) {
            alert("Microphone permission denied or unavailable.");
            setRecording(false);
            setTyping(false);
            return;
        }
        mediaRecorder.current = new MediaRecorder(stream);

        mediaRecorder.current.ondataavailable = (e) => {
            if (e.data.size > 0) {
                e.data.arrayBuffer().then(buffer => ws.current.send(buffer));
            }
        };

        mediaRecorder.current.onstop = () => {
            ws.current.send(new Uint8Array([69, 78, 68])); // b"END"
            stream.getTracks().forEach(track => track.stop());
            setRecording(false);
        };

        mediaRecorder.current.start(250); // Send data every 250ms
    };

    const stopRecording = () => {
        if (mediaRecorder.current && recording) {
            mediaRecorder.current.stop();
        }
    };

    const handleVoiceBtn = () => {
        if (recording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    // --- RENDER WITH React.createElement ---
    return React.createElement("div", {
            style: {position:'relative', width: '100%', height: '100%', display:'flex', flexDirection:'column', flex:1}
        },
        // Back button
        React.createElement("button", {
            onClick: onBack,
            style: {
                position: 'absolute',
                top: 18,
                left: 16,
                zIndex: 30,
                background: "#222",
                color: "#fff",
                border: "none",
                borderRadius: "50%",
                width: 48,
                height: 48,
                fontSize: "1.5em",
                cursor: "pointer",
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: "0 2px 10px #0002"
            },
            "aria-label": "Back",
            title: "Back"
        }, React.createElement("span", {style: {fontSize: "1.6em", marginTop:"-2px"}}, "←")),

        // Chat messages
        React.createElement("div", {className: "chat-messages"},
            messages.map((msg, idx) =>
                React.createElement("div", {key: idx, className: `bubble-row ${msg.from}`},
                    React.createElement("div", {className: `chat-message ${msg.from}`}, msg.message)
                )
            ),
            typing && React.createElement("div", {className: "typing-indicator"}, "thinking..."),
            React.createElement("div", {ref: messagesEndRef})
        ),

        // Voice button and audio
        React.createElement("div", {className: "voice-btn-wrap"},
            React.createElement("button", {
                className: "voice-btn",
                "aria-pressed": recording,
                id: "voice-btn",
                onClick: handleVoiceBtn,
                title: recording ? "Stop" : "Talk"
            }, React.createElement("i", {className: recording ? "fas fa-stop" : "fas fa-microphone"})),
            React.createElement("audio", {ref: botAudioRef, controls: true, style: {display: 'none'}})
        )
    );
}

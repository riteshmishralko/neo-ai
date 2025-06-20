function GreetingScreen2({ showDropdown, setShowDropdown, onDownload, onUpload, onClose }) {
  const [listening, setListening] = React.useState(false);
  const [recording, setRecording] = React.useState(false);
  const ws = React.useRef(null);
  const mediaRecorder = React.useRef(null);
  const botAudioChunks = React.useRef([]);
  const botAudioRef = React.useRef(null);
  const dropdownRef = React.useRef(null);
  const userId = "doctor"; // Or from props

  // Flower image
  const flowerImg = "https://i.imgur.com/mMyZcB2.png";

  // Dropdown close on outside click
  React.useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }
    if (showDropdown) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showDropdown, setShowDropdown]);

  // ---- Icons ----
  const listIcon = (
    React.createElement("svg", { width: 28, height: 28, fill: "none", stroke: "#fff", strokeWidth: 2, viewBox: "0 0 24 24" },
      React.createElement("line", { x1: 4, y1: 6, x2: 20, y2: 6 }),
      React.createElement("line", { x1: 4, y1: 12, x2: 20, y2: 12 }),
      React.createElement("line", { x1: 4, y1: 18, x2: 20, y2: 18 })
    )
  );
  const micIcon = (
    React.createElement("svg", { width: 28, height: 28, fill: "none", stroke: "#fff", strokeWidth: 2, viewBox: "0 0 24 24" },
      React.createElement("rect", { x: 9, y: 2, width: 6, height: 12, rx: 3, fill: "#fff", stroke: "none" }),
      React.createElement("rect", { x: 9, y: 2, width: 6, height: 12, rx: 3 }),
      React.createElement("line", { x1: 12, y1: 18, x2: 12, y2: 22 }),
      React.createElement("path", { d: "M5 11v1a7 7 0 0 0 14 0v-1" })
    )
  );
  const micMutedIcon = (
    React.createElement("svg", { width: 28, height: 28, fill: "none", stroke: "#fff", strokeWidth: 2, viewBox: "0 0 24 24" },
      React.createElement("rect", { x: 9, y: 2, width: 6, height: 12, rx: 3, fill: "#fff", stroke: "none" }),
      React.createElement("rect", { x: 9, y: 2, width: 6, height: 12, rx: 3 }),
      React.createElement("line", { x1: 12, y1: 18, x2: 12, y2: 22 }),
      React.createElement("path", { d: "M5 11v1a7 7 0 0 0 14 0v-1" }),
      React.createElement("line", { x1: 6, y1: 6, x2: 18, y2: 18, stroke: "red", strokeWidth: 2 })
    )
  );
  const closeIcon = (
    React.createElement("svg", { width: 28, height: 28, fill: "none", stroke: "#fff", strokeWidth: 2, viewBox: "0 0 24 24" },
      React.createElement("line", { x1: 6, y1: 6, x2: 18, y2: 18 }),
      React.createElement("line", { x1: 6, y1: 18, x2: 18, y2: 6 })
    )
  );

  // ---- STYLES ----
  React.useEffect(() => {
    if (!document.getElementById("blink-keyframes")) {
      const style = document.createElement("style");
      style.id = "blink-keyframes";
      style.innerHTML = `
        @keyframes blink {
          0%   { box-shadow: 0 0 32px 0 #3336; filter: brightness(1) contrast(1.15);}
          50%  { box-shadow: 0 0 64px 16px #8fa2ff, 0 0 0 4px #232323; filter: brightness(1.25) contrast(1.35);}
          100% { box-shadow: 0 0 32px 0 #3336; filter: brightness(1) contrast(1.15);}
        }
      `;
      document.head.appendChild(style);
    }
  }, []);

  const styles = {
    container: {
      width: "100vw",
      maxWidth: 430,
      minHeight: "100vh",
      background: "#000",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "space-between",
      position: "relative",
      fontFamily: "'Segoe UI', Arial, sans-serif",
      color: "#fff",
      margin: 0,
      padding: 0,
      boxSizing: "border-box"
    },
    greeting: {
      textAlign: "center",
      marginTop: 110,
      marginBottom: 40,
      fontSize: "2rem",
      fontWeight: 400,
      lineHeight: 1.3
    },
    flower: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    },
    flowerImg: {
      width: 220,
      height: 220,
      borderRadius: "50%",
      objectFit: "cover",
      background: "#fff",
      filter: "brightness(0.95) contrast(1.15)",
      boxShadow: "0 0 32px 0 #3336",
      animation: listening ? "blink 1s infinite" : "none",
      transition: "box-shadow 0.3s, filter 0.3s"
    },
    bottomBar: {
      width: "100%",
      display: "flex",
      justifyContent: "space-around",
      alignItems: "center",
      paddingBottom: 34,
      marginTop: 30
    },
    circleBtn: {
      width: 68,
      height: 68,
      background: "#222",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      borderRadius: "50%",
      margin: "0 8px",
      boxShadow: "0 2px 12px #1114",
      border: "none",
      cursor: "pointer",
      transition: "background 0.2s"
    }
  };

  // Dropdown styles
  const dropdownStyle = {
    position: "absolute",
    bottom: 90,
    left: "0",
    width: 220,
    background: "#222",
    borderRadius: "18px",
    boxShadow: "0 6px 24px #000a",
    padding: "12px 0",
    zIndex: 100,
    display: "flex",
    flexDirection: "column",
    alignItems: "stretch"
  };
  const itemStyle = {
    font: "inherit",
    color: "#fff",
    background: "none",
    border: "none",
    borderBottom: "1px solid #444",
    padding: "17px 22px",
    textAlign: "left",
    cursor: "pointer",
    fontSize: "1.08rem"
  };
  const lastItemStyle = {...itemStyle, borderBottom: "none"};
  const buttonDropdownWrapperStyle = {position: "relative", display:"inline-block"};

  // ---- WebSocket & Audio logic ----
  React.useEffect(() => {
    var protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    console.log("protocol");
    console.log(protocol);
    ws.current = new WebSocket(`${protocol}://${location.host}/ws?user_id=${userId}`);
    ws.current.binaryType = "arraybuffer";

    ws.current.onopen = () => {
      console.log("WebSocket connection established (GreetingScreen2)");
    };

    ws.current.onmessage = async (event) => {
      if (event.data instanceof ArrayBuffer) {
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

  // Start recording (and send audio to websocket)
  const startRecording = async () => {
    setRecording(true);
    botAudioChunks.current = [];
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      alert("Microphone permission denied or unavailable.");
      setRecording(false);
      setListening(false);
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

  const handleMicToggle = () => {
    setListening(listen => {
      const next = !listen;
      if (next) {
        startRecording();
      } else {
        stopRecording();
      }
      return next;
    });
  };

  return React.createElement("div", {style: {...styles.container, position:"relative"}},
    React.createElement("div", {style: styles.greeting},
      React.createElement("div", null, "Hi"),
      React.createElement("div", null,
        "Let's know ",
        React.createElement("span", {style: {color: "#b5b5e5"}}, "each"),
        " ",
        React.createElement("span", {style: {color: "#888bb5"}}, "other")
      )
    ),
    React.createElement("div", {style: styles.flower},
      React.createElement("img", {
        src: flowerImg,
        style: styles.flowerImg,
        alt: "Flower",
        title: listening ? "Listening..." : "Mic muted"
      })
    ),
    React.createElement("div", {style: styles.bottomBar},
      React.createElement("div", {style: buttonDropdownWrapperStyle},
        React.createElement("button", {
          style: styles.circleBtn,
          onClick: () => setShowDropdown(open => !open)
        }, listIcon),
        showDropdown && React.createElement("div", {ref: dropdownRef, style: dropdownStyle},
          React.createElement("button", {
            style: itemStyle,
            onClick: () => { onDownload(); setShowDropdown(false); }
          }, "Download Report"),
          React.createElement("button", {
            style: lastItemStyle,
            onClick: () => { onUpload(); setShowDropdown(false); }
          }, "Upload New Report")
        )
      ),
      React.createElement("div", {style: {display: "flex", flexDirection: "column", alignItems: "center"}},
        React.createElement("button", {
          style: styles.circleBtn,
          onClick: handleMicToggle,
          title: listening ? "Click to mute" : "Click to listen"
        }, listening ? micIcon : micMutedIcon),
        React.createElement("div", {style: {fontSize: "0.93rem", color: listening ? "#79ffb2" : "#d55", marginTop: 5}},
          listening ? (recording ? "Listening..." : "Preparing...") : "Mic muted"
        ),
        React.createElement("audio", {ref: botAudioRef, controls: true, style: {display: 'none'}})
      ),
      React.createElement("button", {
        style: styles.circleBtn,
        onClick: onClose
      }, closeIcon)
    )
  );
}

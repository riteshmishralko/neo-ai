function GreetingScreen3({ onUpload, onClose }) {
  const [file, setFile] = React.useState(null);
  const fileInputRef = React.useRef();

  const flowerImg = "https://i.imgur.com/mMyZcB2.png";

  const cardStyle = {
    display: "flex",
    alignItems: "center",
    background: "#aaa8",
    borderRadius: 20,
    padding: "4px 27px",
    boxShadow: "0 2px 8px #0001",
    width: "89%",
    maxWidth: 370,
    minHeight: 54,
    cursor: "pointer",
    transition: "background 0.13s",
    border: file ? "2px solid #4b4" : "2px solid transparent"
  };

  // The bar holding close and start button, aligned like a footer
  const footerBarStyle = {
    width: "94%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: 16,   // space between close and start
    margin: "0 0 38px 0"
  };

  // Modern close circle in row (smaller than sticky close, but just like a button)
  const closeCircleStyle = {
    width: 54,
    height: 54,
    background: "#222",
    border: "none",
    borderRadius: "50%",
    color: "#fff",
    fontSize: "1.8rem",
    fontWeight: 300,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    outline: "none",
    boxShadow: "0 2px 10px #0002",
    cursor: "pointer",
    transition: "background 0.15s"
  };

  // Start/submit button
  const startBtnStyle = {
    flex: 1,
    minWidth: 140,
    maxWidth: 280,
    background: file ? "#fff" : "#ccc",
    color: "#232323",
    border: "none",
    borderRadius: 34,
    fontSize: "1.7rem",
    padding: "11px 0",
    fontWeight: 500,
    cursor: file ? "pointer" : "not-allowed",
    boxShadow: "0 4px 16px #0001",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10
  };

  // Button icon: Right arrow SVG
  const arrowIcon = React.createElement("svg", { width: 32, height: 32, viewBox: "0 0 24 24", fill: "none", stroke: "#232323", strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round", style: { verticalAlign: "middle" } }, 
    React.createElement("path", { d: "M5 12h14" }),
    React.createElement("path", { d: "M13 5l7 7-7 7" })
  );

  return React.createElement(
    "div",
    {
      style: {
        width: "100vw",
        maxWidth: 430,
        minHeight: "100vh",
        background: "#000",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        position: "relative",
        fontFamily: "'Segoe UI', Arial, sans-serif",
        color: "#fff",
        margin: 0,
        padding: 0,
        boxSizing: "border-box"
      }
    },
   
    // Greeting
    React.createElement("div", {
      style: {
        marginTop: 128,
        marginBottom: 18,
        fontSize: "1.5rem",
        fontWeight: 350,
        textAlign: "center",
        lineHeight: 1.1
      }
    },
      React.createElement("div", null, "Hi, click below"),
      React.createElement("div", null, "And Upload Report for better understanding")
    ),

    // Flower image
    React.createElement("div", { style: { margin: "0 0 40px 0", display: "flex", justifyContent: "center", alignItems: "center" } },
      React.createElement("img", {
        src: flowerImg,
        alt: "Flower",
        style: {
          width: 220,
          height: 220,
          borderRadius: "50%",
          objectFit: "cover",
          background: "#fff",
          filter: "brightness(0.95) contrast(1.15)",
          boxShadow: "0 0 32px 0 #3336"
        }
      })
    ),

    // PDF upload card
    React.createElement("div", { style: { marginTop: "auto", marginBottom: 18, width: "100%", display: "flex", justifyContent: "center" } },
      React.createElement("div", {
        style: cardStyle,
        onClick: () => { if (fileInputRef.current) fileInputRef.current.click(); },
        title: "Upload a PDF Report"
      },
        React.createElement("div", {
          style: {
            width: 38,
            height: 38,
            marginRight: 14,
            background: "#ddd",
            borderRadius: 10,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundImage: "url('https://cdn-icons-png.flaticon.com/512/1828/1828826.png')",
            backgroundSize: "70%",
            backgroundRepeat: "no-repeat",
            backgroundPosition: "center"
          }
        }),
        React.createElement("div", { style: { display: "flex", flexDirection: "column" } },
          !file
            ? [
                React.createElement("span", { key: 1, style: { color: "#232323", fontWeight: "bold", fontSize: "1rem" } }, "Click to Upload PDF"),
                React.createElement("span", { key: 2, style: { color: "#232323cc", fontSize: "0.93rem", marginTop: 2 } }, "Upload Updated Report, while we analyze")
              ]
            : [
                React.createElement("span", { key: 1, style: { color: "#235623", fontWeight: "bold", fontSize: "1rem" } }, file.name),
                React.createElement("span", { key: 2, style: { color: "#232323cc", fontSize: "0.88rem", marginTop: 2 } }, "PDF ready to upload!")
              ]
        ),
        // Hidden file input
        React.createElement("input", {
          type: "file",
          accept: "application/pdf",
          ref: fileInputRef,
          style: { display: "none" },
          onChange: e => setFile(e.target.files[0])
        })
      )
    ),

    // Bottom horizontal row: Close and Start
    React.createElement("div", { style: footerBarStyle },
      // CLOSE CIRCLE
      React.createElement("button", {
        style: closeCircleStyle,
        onClick: onClose,
        title: "Cancel and return"
      }, "×"),
      // START/SUBMIT BUTTON WITH ICON
      React.createElement("button", {
        style: startBtnStyle,
        onClick: () => file && onUpload(file),
        disabled: !file
      },
        "Upload",
        arrowIcon
      )
    )
  );
}
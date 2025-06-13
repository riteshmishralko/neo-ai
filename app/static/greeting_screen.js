function GreetingScreen({ onStart }) {
  const flowerImg = "https://i.imgur.com/mMyZcB2.png";
  const labIconImg = "https://cdn-icons-png.flaticon.com/512/1828/1828826.png";

  const styles = {
    container: {
      width: "100vw",
      maxWidth: 430,
      height: "100vh",
      background: "#000",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      position: "relative",
      fontFamily: "'Segoe UI', Arial, sans-serif",
      color: "#fff",
      margin: 0,
      padding: 0,
      boxSizing: "border-box"
    },
    greeting: {
      textAlign: "center",
      marginTop: 90,
      fontSize: "2rem",
      fontWeight: 400,
      lineHeight: 1.2
    },
    flower: {
      margin: "48px 0 32px 0",
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
      boxShadow: "0 0 32px 0 #3336"
    },
    labReport: {
      display: "flex",
      alignItems: "center",
      background: "#aaa8",
      padding: "12px 16px",
      borderRadius: 25,
      width: "86%",
      maxWidth: 370,
      margin: "0 auto 28px auto",
      boxShadow: "0 2px 8px 0 #0002"
    },
    labIcon: {
      width: 38,
      height: 38,
      background: "#ddd",
      borderRadius: 10,
      marginRight: 14,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      backgroundSize: "70%",
      backgroundRepeat: "no-repeat",
      backgroundPosition: "center",
      backgroundImage: `url(${labIconImg})`
    },
    labText: {
      display: "flex",
      flexDirection: "column"
    },
    labTitle: {
      color: "#232323",
      fontWeight: "bold",
      fontSize: "1.1rem"
    },
    labDesc: {
      color: "#232323cc",
      fontSize: "0.96rem",
      marginTop: 2,
      fontWeight: 400
    },
    startBtn: {
      marginTop: 20,
      marginBottom: 30,
      width: 180,
      maxWidth: "70vw",
      background: "#fff",
      color: "#232323",
      border: "none",
      borderRadius: 36,
      fontSize: "1.5rem",
      padding: "14px 0",
      fontWeight: 500,
      cursor: "pointer",
      boxShadow: "0 4px 16px #0001",
      transition: "background 0.15s"
    }
  };

  return React.createElement("div", {style: styles.container},
    React.createElement("div", {style: { ...styles.topBar, position: "absolute", top: 20, left: 20}}, ""),

    React.createElement("div", {style: styles.greeting},
      React.createElement("span", null, "Hi "),
      React.createElement("span", null, "Good Morning!")
    ),
    React.createElement("div", {style: styles.flower},
      React.createElement("img", {src: flowerImg, style: styles.flowerImg, alt: "Flower"})
    ),
  
    React.createElement("button", {
      style: styles.startBtn,
      onClick: onStart
    }, "Start")
  );
}
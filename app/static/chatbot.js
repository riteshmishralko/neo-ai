window.onload = function () {
    const userid = prompt("Please Enter your user id");
    var auth_token = ""
    var db = null


    function load_chat_from_s3() {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        var raw = JSON.stringify({
            "user_id": userid
        });

        var requestOptions = {
            method: 'POST',
            headers: myHeaders,
            body: raw,
            redirect: 'follow'
        };

        fetch(sentibot_url + "load_s3chat_to_firebase", requestOptions)
            .then(response => response.text())
            .then(result => {
                console.log(result)
                result = JSON.parse(result)
                auth_token = result.firebase_auth_token
                // Initialize Firebase
                firebase.initializeApp(firebaseConfig);
                firebase.auth().signInWithCustomToken(auth_token)
                    .then((userCredential) => {
                        // Your auth.uid will now be "your-user-id-in-db"
                        console.log(userCredential)
                        db = firebase.database();
                        console.log(db);
                        fetchChat()
                    })
                    .catch((error) => {
                        console.log("Error signing in with custom token:", error);
                    });

            })
            .catch(error => console.log('error', error));
    }
    load_chat_from_s3()


    function fetchChat() {
        const fetchChat = db.ref("health_assist_chats/" + userid);
        fetchChat.on("child_added", function (snapshot) {
            const messages = snapshot.val();
            const messagesContainer = document.getElementById("messages");
            if (messages.sender === 'bot' && messages.typing_indicator) {
                // Display typing indicator
                const typingIndicator = `<li><span>Bot: </span>${messages.message}</li><br>`;
                messagesContainer.innerHTML += typingIndicator;
            } else {
                const message = `<li><span>${messages.sender}: </span>${messages.message}</li><br>`;
                // append the message on the page
                messagesContainer.innerHTML += message;
                if (messages.sender == 'bot' && messages.product.display) {
                    const products = messages.product.tests;

                    const productContainer = document.createElement("li");
                    productContainer.innerHTML = `<span>Recommended Tests:</span>`;

                    // Create a table
                    const productTable = document.createElement("table");

                    // Create table header
                    const tableHeader = document.createElement("tr");
                    tableHeader.innerHTML = `<th>Test ID</th><th>Test Name</th><th>Test Type</th>`;
                    productTable.appendChild(tableHeader);

                    // Add products to the table
                    products.forEach(product => {
                        const productRow = document.createElement("tr");
                        productRow.innerHTML = `<td>${product.test_id}</td><td>${product.test_name}</td><td>${product.test_type}</td>`;
                        productTable.appendChild(productRow);
                    });

                    productContainer.appendChild(productTable);
                    messagesContainer.appendChild(productContainer);

                } else if (messages.sender == 'bot' && messages.sales_support.display) {
                    const salesContainer = document.createElement("li");
                    salesContainer.innerHTML = `<span>${messages.sales_support.button_text}: ${messages.sales_support.link}</span>`;
                    messagesContainer.appendChild(salesContainer);

                } else if (messages.sender == 'bot' && messages.customer_support.display) {
                    const customer_supportContainer = document.createElement("li");
                    customer_supportContainer.innerHTML = `<span>${messages.customer_support.button_text}: ${messages.customer_support.link}</span>`;
                    messagesContainer.appendChild(customer_supportContainer);

                }
            }

        });

    }


    document.getElementById("message-btn").addEventListener("click", sendMessage);
    function sendMessage(e) {
        e.preventDefault();
        // get values to be submitted
        const timestamp = String(parseInt(Date.now() / 1000));
        const messageInput = document.getElementById("message-input");
        const message = messageInput.value;
        const sender = "user"
        // clear the input box
        messageInput.value = "";

        // create db collection and send in the data
        if (db != null) {
            db.ref("health_assist_chats/" + userid + "/" + timestamp).set({
                sender,
                message,
                timestamp
            });
        }

    }

    document.getElementById("close_chat").addEventListener("click", close_chat);
    function close_chat(e) {
        e.preventDefault();
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        var raw = JSON.stringify({
            "user_id": userid
        });

        var requestOptions = {
            method: 'POST',
            headers: myHeaders,
            body: raw,
            redirect: 'follow'
        };

        fetch(sentibot_url + "close_chat", requestOptions)
            .then(response => response.text())
            .then(result => console.log(result))
            .catch(error => console.log('error', error));
        location.reload()
    }
}


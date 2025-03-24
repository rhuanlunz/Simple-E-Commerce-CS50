const form = document.forms[0];

form.addEventListener("submit", async function(e) {
	e.preventDefault();

	// Get form user data
	const credsForm = new FormData(this);

	// Send user data
	const msg = await sendForm(credsForm, globalThis.location.href);
	
	// Show notification toast
	notify(msg["type"], msg["message"]);

	// Handle error messages
	if (msg["type"] === "error") {
		switch(msg["type"]) {
			case "Invalid email!" || "Email required!":
				this.elements["email"].focus();
				break;
			case "Wrong email or password!" || "Password required":
				this.elements["password"].focus();
				break;
		}
	}
	else {
		globalThis.location.assign("/user");
	}
});

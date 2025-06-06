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
		switch(msg) {
			case "Username required!" || "Username already exists!":
				this.elements["username"].focus();
				break;
			case "Invalid email!" || "Email required!" || "Email already exists!":
				this.elements["email"].focus();
				break;
			case "Password required":
				this.elements["password"].focus();
				break;
			case "Passwords don't match!" || "Password confirmation required":
				this.elements["confirmation"].focus();
				break;
		}
	}
	else {
		globalThis.location.assign("/user");
	}
});

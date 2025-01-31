const form = document.forms[0];

form.addEventListener("submit", async function(e) {
	e.preventDefault();

	// Get form user data
	const credsForm = new FormData(this);

	// Send user data
	const msg = await sendForm(credsForm, globalThis.location.href, "/user");
	
	// Handle return messages
	switch(msg) {
		case "Invalid email!" || "Email required!":
			this.elements["email"].focus();
			break;
		case "Wrong email or password!" || "Password required":
			this.elements["password"].focus();
			break;
	}
});

document.querySelector("#send").addEventListener("click", async () => {
	// Get user data
	const email = document.querySelector("#email");
	const password = document.querySelector("#password");	

	// Focus missing inputs
	if (!email.value) {
		email.focus();
	}
	else if (!password.value) {
		password.focus();
	}

	// Send user data
	const msg = await send({email: email.value, password: password.value});
	
	// Handle return messages
	switch(msg) {
		case "Invalid email!":
			email.focus();
			break;
		case "Wrong email or password!":
			password.focus();
			break;
	}
});

const form = document.forms["edit"];
const delForm = document.forms["delete"];

form.addEventListener("submit", async function(e) {
	e.preventDefault();

	const credsForm = new FormData(this);

	const url = globalThis.location.href;

	const msg = await sendForm(credsForm, url);

	notify(msg["type"], msg["message"]);

	if (msg["type"] === "error") {
		switch(msg["message"]) {
			case "Username required!" || "Username already exists!":
				this.elements["username"].focus();
				break;
			case "Invalid email!" || "Email required!" || "Email already exists!":
				this.elements["email"].focus();
				break;
			case "New password must be in 3 to 128 characters!":
				this.elements["password"].focus();
				break;
		}
	}
	else {
		globalThis.location.reload();
	}
});

delForm.addEventListener("submit", async function(e) {
	e.preventDefault();

	bootstrap.Modal.getInstance("#deleteAccountModal").hide();

	const credsForm = new FormData(this);

	const msg = await sendForm(credsForm, "/user/delete");
	
	notify(msg["type"], msg["message"]);

	if (msg["type"] === "error") {
		switch(msg) {
			case "Wrong password!":
				this.elements["password"].focus();
				break;
		}
	}
	else {
		globalThis.location.assign("/login");
	}
});

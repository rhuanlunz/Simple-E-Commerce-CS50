const form = document.forms["edit"];
const delForm = document.forms["delete"];

form.addEventListener("submit", async function(e) {
	e.preventDefault();

	const credsForm = new FormData(this);

	const url = globalThis.location.href;

	const msg = await sendForm(credsForm, url, url);

	switch(msg) {
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
});

delForm.addEventListener("submit", async function(e) {
	e.preventDefault();

	const credsForm = new FormData(this);

	const msg = await sendForm(credsForm, globalThis.location.href + "/delete", "/login");

	switch(msg) {
		case "Wrong password!":
			this.elements["password"].focus();
			break;
	}

	bootstrap.Modal.getInstance("#deleteAccountModal").hide();
});

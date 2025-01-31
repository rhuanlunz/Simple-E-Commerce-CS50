const showBtns = document.querySelectorAll(".show");

showBtns.forEach(btn => {
	btn.addEventListener("click", function() {
		const input = this.parentNode.querySelector("input[type='password'], input[type='text']");
		
		if (input.type === "password") {
			input.type = "text";
			this.innerHTML = "visibility";
		} else {
			input.type = "password";
			this.innerHTML = "visibility_off";
		}
	});
});

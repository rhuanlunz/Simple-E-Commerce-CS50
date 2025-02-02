const addCartBtns = document.querySelectorAll(".addCart");

addCartBtns.forEach((btn) => {
	btn.addEventListener("click", async function() {
		try {
			const response = await fetch("/user/cart/add", {
				method: "POST",
				body: JSON.stringify({"product_id": this.parentNode.parentNode.parentNode.parentNode.id}),
				headers: {
					"Content-Type": "application/json"
				}
			});
			
			if (!response.ok)
				throw new Error(`Status code: ${response.code}`);
			
			const data = await response.text();

			console.log(data);
		} catch(error) {
			console.error(`Error: ${error}`);
		}
	});
});


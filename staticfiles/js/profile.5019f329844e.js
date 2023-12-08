function loading() {
    // Check if group_code is valid
    var group_code = document.getElementById("group_code");
    if (group_code) {
        if (group_code.value.length < 1) {
            console.log("Errors");
        } else {
            console.log("No errors");
            var loading = document.getElementById("loading");
            loading.style.display = "block";
            
            var form = document.getElementById('code_form');
            form.addEventListener("submit", (e) => {
                e.preventDefault();

                setTimeout(function () {
                    console.log("Passes");
                }, 2000);

                e.defaultPrevented = false;
            });
        }
    }

}
function handleServiceChange() {
    const val = document.getElementById('serviceFilter').value;
    let rows = document.querySelectorAll('#tableServiceFilter tbody tr');

    console.log(val);
    rows.forEach((row) => {
        const service = row.cells[2].textContent;
        console.log(service);
        if (val === "" || val === service) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
};

document.getElementById('serviceFilter').addEventListener('change', handleServiceChange);
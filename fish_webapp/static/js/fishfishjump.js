function logout() {
    $.ajax({
        url: "/supervisor/logout",
        type: "POST"
    });
}
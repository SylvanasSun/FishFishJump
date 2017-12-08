function logout() {
    $.ajax({
        url: "/supervisor/user/logout",
        type: "POST"
    });
}
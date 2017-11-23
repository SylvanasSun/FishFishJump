function logout() {
    $.ajax({
        url: "/logout",
        type: "POST"
    });
}
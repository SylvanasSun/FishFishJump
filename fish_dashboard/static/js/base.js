function logout() {
    $.ajax({
        url: "/user/logout",
        type: "POST"
    });
}
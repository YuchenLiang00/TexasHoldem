document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault(); // 阻止表单默认提交行为

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    // 发送请求到后端进行验证
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: username, password: password})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/home'; // 登录成功，跳转到主页
        } else {
            alert('Login failed: ' + data.message); // 登录失败，显示错误信息
        }
    })
    .catch(error => console.error('Error:', error));
});

// pages/Login.jsx
import Form from "../components/forms/Form"

function Login() {
    return <Form route="/api/token" method="login" />
}

export default Login
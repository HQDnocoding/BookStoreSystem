# Tạo URL Expose ra Internet để Đăng Ký VNPay

## Cài đặt LocalTunnel

Trước tiên, bạn cần cài đặt LocalTunnel bằng npm:

```bash
npm install -g localtunnel
```

## Tạo URL Public

Chạy lệnh sau để tạo một liên kết public, đảm bảo rằng firewall đã được tắt và không sử dụng 1.1.1.1:

```bash
lt --port 5001 --subdomain huymanhdatbookstoresystemcnpm
```

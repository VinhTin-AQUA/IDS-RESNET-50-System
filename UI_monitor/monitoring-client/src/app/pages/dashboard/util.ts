export function getRandomIP() {
    return `${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}`;
}

export function getRandomPort() {
    return Math.floor(Math.random() * (65535 - 1024) + 1024); // Cổng từ 1024 đến 65535
}

export function getRandomProtocol() {
    const protocols = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "FTP", "SSH"];
    return protocols[Math.floor(Math.random() * protocols.length)];
}

export function getRandomTimestamp() {
    // return new Date(Date.now() - Math.floor(Math.random() * 1000000000)).toISOString();
    return new Date().toISOString();
}

export function getRandomPrediction() {
    return Math.random() > 0.5 ? "Benign" : "Malicious";
}

export function generateRandomNetworkData() {
    return {
        src_ip: getRandomIP(),
        dst_ip: getRandomIP(),
        src_port: getRandomPort(),
        dst_port: getRandomPort(),
        protocol: getRandomProtocol(),
        timestamp: getRandomTimestamp(),
        prediction: getRandomPrediction()
    };
}


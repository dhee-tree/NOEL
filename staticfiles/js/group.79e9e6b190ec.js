const copyToClipboard = async () => {
  try {
    const element = document.querySelector(".invite-code");
    await navigator.clipboard.writeText(element.textContent);
    alert("Copied invite code to clipboard!");
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
  }
};

// Share invite code
function encodeMessage(message) {
    return encodeURIComponent(message);
}

function createWhatsAppLink(message) {
    const encodedMessage = encodeMessage(message);
    return `https://api.whatsapp.com/send?text=${encodedMessage}`;
}

const shareMessage = "Hello, join me on NOEL. My group name is {{group}}. Use this code {{group.group_code}} to join my group. Register with https://noel.ighomena.me/auth/register/";

const whatsappLink = createWhatsAppLink(shareMessage);

document.getElementById('whatsappLink').setAttribute('href', whatsappLink);
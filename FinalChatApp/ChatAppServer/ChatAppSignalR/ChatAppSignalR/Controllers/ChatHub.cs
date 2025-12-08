using Microsoft.AspNetCore.SignalR;

public class ChatHub : Hub
{
    private static Dictionary<string, string> OnlineUsers = new Dictionary<string, string>();

    public async Task RegisterUser(string username)
    {
        OnlineUsers[username] = Context.ConnectionId;
        await Clients.Client(OnlineUsers[username]).SendAsync("ReceiveMessage", "Server", $"Welcome {username}");

        return;
    }


    public async Task SendPrivateMessage(string toUser, string fromUser, string message)
    {
        if (OnlineUsers.TryGetValue(toUser, out string connectionId))
        {
            

            await Clients.Client(connectionId).SendAsync("ReceiveMessage", fromUser, message);
        }
    }
}

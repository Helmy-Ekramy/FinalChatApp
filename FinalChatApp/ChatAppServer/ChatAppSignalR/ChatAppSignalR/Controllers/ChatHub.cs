using Microsoft.AspNetCore.SignalR;
using System.Collections.Concurrent;

public class ChatHub : Hub
{
    // Store online users: username -> connectionId
    private static ConcurrentDictionary<string, string> OnlineUsers = new ConcurrentDictionary<string, string>();

    // Store groups: groupName -> list of usernames
    private static ConcurrentDictionary<string, List<string>> Groups = new ConcurrentDictionary<string, List<string>>();

    // Store user to groups mapping: username -> list of groupNames
    private static ConcurrentDictionary<string, List<string>> UserGroups = new ConcurrentDictionary<string, List<string>>();

    public async Task RegisterUser(string username)
    {
        // Add or update user
        OnlineUsers[username] = Context.ConnectionId;

        // Initialize user groups if not exists
        if (!UserGroups.ContainsKey(username))
        {
            UserGroups[username] = new List<string>();
        }

        // Send welcome message
        await Clients.Client(Context.ConnectionId).SendAsync("ReceiveMessage", "Server", $"Welcome {username}!");

        // Broadcast updated user list to all clients
        await BroadcastOnlineUsers();

        // Send user's groups
        await SendUserGroups(username);
    }

    public async Task GetOnlineUsers()
    {
        var usernames = OnlineUsers.Keys.ToList();
        await Clients.Caller.SendAsync("UpdateOnlineUsers", usernames);
    }

    public async Task GetGroups()
    {
        var username = GetUsernameByConnectionId(Context.ConnectionId);
        if (username != null && UserGroups.ContainsKey(username))
        {
            var userGroupsList = UserGroups[username];
            await Clients.Caller.SendAsync("UpdateGroups", userGroupsList);
        }
    }

    public async Task SendPrivateMessage(string toUser, string fromUser, string message)
    {
        if (OnlineUsers.TryGetValue(toUser, out string? connectionId))
        {
            await Clients.Client(connectionId).SendAsync("ReceiveMessage", fromUser, message);
        }
    }

    public async Task CreateGroup(string groupName, List<string> members)
    {
        if (string.IsNullOrWhiteSpace(groupName) || members == null || members.Count == 0)
        {
            return;
        }

        // Create or update group
        Groups[groupName] = members;

        // Update each member's group list
        foreach (var member in members)
        {
            if (!UserGroups.ContainsKey(member))
            {
                UserGroups[member] = new List<string>();
            }

            if (!UserGroups[member].Contains(groupName))
            {
                UserGroups[member].Add(groupName);
            }

            // Notify member about new group
            if (OnlineUsers.TryGetValue(member, out string? connectionId))
            {
                await Clients.Client(connectionId).SendAsync("UpdateGroups", UserGroups[member]);
            }
        }
    }

    public async Task SendGroupMessage(string groupName, string fromUser, string message)
    {
        if (!Groups.TryGetValue(groupName, out List<string>? members))
        {
            return;
        }

        // Send message to all group members except sender
        foreach (var member in members)
        {
            if (member != fromUser && OnlineUsers.TryGetValue(member, out string? connectionId))
            {
                await Clients.Client(connectionId).SendAsync("ReceiveGroupMessage", groupName, fromUser, message);
            }
        }
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        // Find and remove disconnected user
        var disconnectedUser = OnlineUsers.FirstOrDefault(x => x.Value == Context.ConnectionId).Key;

        if (!string.IsNullOrEmpty(disconnectedUser))
        {
            OnlineUsers.TryRemove(disconnectedUser, out _);

            // Broadcast updated user list
            await BroadcastOnlineUsers();
        }

        await base.OnDisconnectedAsync(exception);
    }

    private async Task BroadcastOnlineUsers()
    {
        var usernames = OnlineUsers.Keys.ToList();
        await Clients.All.SendAsync("UpdateOnlineUsers", usernames);
    }

    private async Task SendUserGroups(string username)
    {
        if (UserGroups.ContainsKey(username))
        {
            var userGroupsList = UserGroups[username];
            if (OnlineUsers.TryGetValue(username, out string? connectionId))
            {
                await Clients.Client(connectionId).SendAsync("UpdateGroups", userGroupsList);
            }
        }
    }

    private string? GetUsernameByConnectionId(string connectionId)
    {
        return OnlineUsers.FirstOrDefault(x => x.Value == connectionId).Key;
    }
}
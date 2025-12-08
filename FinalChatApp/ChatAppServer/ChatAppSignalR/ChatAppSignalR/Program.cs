
using ChatAppSignalR.Controllers;

namespace ChatAppSignalR
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);
            builder.Services.AddSignalR();
            var app = builder.Build();
            app.MapHub<ChatHub>("/chatHub");

            // Force HTTP only
            app.Urls.Clear();
            app.Urls.Add("http://localhost:5283");

            app.Run();


        }
    }
}

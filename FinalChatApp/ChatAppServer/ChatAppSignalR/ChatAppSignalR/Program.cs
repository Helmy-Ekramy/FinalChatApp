namespace ChatAppSignalR
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Add SignalR services
            builder.Services.AddSignalR();

            // Add CORS for Python client
            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowAll", policy =>
                {
                    policy.AllowAnyOrigin()
                          .AllowAnyMethod()
                          .AllowAnyHeader();
                });
            });

            var app = builder.Build();

            // Use CORS
            app.UseCors("AllowAll");

            // Map SignalR hub
            app.MapHub<ChatHub>("/chatHub");

            // Force HTTP only
            app.Urls.Clear();
            app.Urls.Add("http://localhost:5283");

            Console.WriteLine("SignalR Chat Server running on http://localhost:5283");
            Console.WriteLine("Hub endpoint: http://localhost:5283/chatHub");

            app.Run();
        }
    }
}
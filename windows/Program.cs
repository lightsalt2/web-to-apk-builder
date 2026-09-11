using Microsoft.Web.WebView2.WinForms;
using System.Text.Json;

namespace WebToApp;

internal static class Program
{
    [STAThread]
    static void Main()
    {
        ApplicationConfiguration.Initialize();
        var configPath = Path.Combine(AppContext.BaseDirectory, "appsettings.json");
        var config = JsonSerializer.Deserialize<AppConfig>(File.ReadAllText(configPath)) ?? new AppConfig();
        Application.Run(new MainForm(config));
    }
}

internal sealed class AppConfig
{
    public string AppName { get; set; } = "Web App";
    public string StartUrl { get; set; } = "https://example.com";
}

internal sealed class MainForm : Form
{
    private readonly AppConfig _config;
    private readonly WebView2 _webView = new() { Dock = DockStyle.Fill };

    public MainForm(AppConfig config)
    {
        _config = config;
        Text = config.AppName;
        Width = 1280;
        Height = 800;
        StartPosition = FormStartPosition.CenterScreen;
        Controls.Add(_webView);
        Load += OnLoadAsync;
    }

    private async void OnLoadAsync(object? sender, EventArgs e)
    {
        await _webView.EnsureCoreWebView2Async();
        _webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;
        _webView.CoreWebView2.Settings.AreDevToolsEnabled = false;
        _webView.Source = new Uri(_config.StartUrl);
    }
}

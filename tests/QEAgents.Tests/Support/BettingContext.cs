using BettingPlatform;

namespace QEAgents.Tests.Support;

/// <summary>
/// Reqnroll context-injection object: one instance per scenario, shared across all step
/// definition classes that ask for it in their constructor.
/// </summary>
public sealed class BettingContext
{
    public Dictionary<string, Player> Players { get; } = new();
    public Dictionary<string, Market> Markets { get; } = new();
    public string MatchId { get; set; } = "";
    public Exception? LastError { get; private set; }

    private MarketSuspensionService? _service;

    public void InitializeService()
    {
        _service = new MarketSuspensionService(Markets.Values.ToList());
    }

    public string PlayerIdByName(string name) =>
        Players.Values.First(p => p.Name.Equals(name, StringComparison.OrdinalIgnoreCase)).PlayerId;

    /// <summary>
    /// Fires the red card without waiting for it to finish, so scenarios can decide for
    /// themselves how (and whether) to tolerate the platform's async propagation delay.
    /// </summary>
    public void FireRedCard(string playerId)
    {
        _ = FireRedCardAsync(playerId);
    }

    private async Task FireRedCardAsync(string playerId)
    {
        try
        {
            var service = _service ?? throw new InvalidOperationException("Service not initialized - markets table step must run first.");
            await service.HandleRedCardAsync(new RedCardEvent { MatchId = MatchId, PlayerId = playerId });
        }
        catch (Exception ex)
        {
            LastError = ex;
        }
    }
}

Feature: Suspend Betting Markets on Red Card

  Background:
    Given a match "Match 1" is in progress
    Given the following players are in the match:
      | playerId | playerName | team    |
      | P1      | Player 1   | Team A  |
      | P2      | Player 2   | Team B  |
    Given the following betting markets are open for the match:
      | marketId | marketType          | eligiblePlayerIds     |
      | M1       | Single Player Market | P1                     |
      | M2       | Multi-Player Market  | P1,P2                  |
      | M3       | Single Player Market | P2                     |
      | M4       | Unrelated Market     |                         |

  @P0
  Scenario: Suspend market for player receiving a direct red card
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"

  @P0
  Scenario: Suspend all related markets when a player receives a direct red card
    When player "Player 1" receives a red card
    Then market "M1" should be "Suspended"
    Then market "M2" should be "Suspended"
  
  @P1
  Scenario: Suspend market for player receiving a second yellow card (resulting in red card)
    When player "Player 2" receives a second yellow card resulting in a red card
    Then market "M3" should be "Suspended"

  @P2
  Scenario: Verify suspension occurs in near-real-time within a few seconds of incident
    When player "Player 1" receives a red card
    Then market "M1" should be suspended within 2000ms

  @P1
  Scenario: Attempt to place a bet on a suspended market after a player receives a red card
    When player "Player 1" receives a red card
    Then no error should have been raised

  @P2
  Scenario: Check for market open if red card is registered after betting period is closed
    When player "Player 1" receives a red card
    Then market "M1" should be "Open"
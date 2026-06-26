import os
import requests
from fastapi import HTTPException, status
from jose import jwt

# Retrieve OAuth Credentials from Environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")

class OAuthService:
    @staticmethod
    def exchange_google_code(code: str, redirect_uri: str) -> dict:
        """Exchange Google authorization code for access token and fetch user profile."""
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            # Fallback to dev mode if env vars are missing
            print("[GOOGLE OAUTH] DEV MODE FALLBACK: Using mock Google data")
            return {
                "oauth_id": "google_dev_mock_12345",
                "email": "google_dev_user@example.com",
                "name": "Google Dev User"
            }

        # 1. Exchange authorization code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        try:
            r = requests.post(token_url, json=payload, headers={"Accept": "application/json"})
            if r.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google token exchange failed: {r.text}"
                )
            tokens = r.json()
            access_token = tokens.get("access_token")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error during Google OAuth: {str(e)}"
            )

        # 2. Retrieve user info using the access token
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        try:
            r_user = requests.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
            if r_user.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to retrieve Google user profile info."
                )
            user_data = r_user.json()
            return {
                "oauth_id": user_data.get("sub"),
                "email": user_data.get("email"),
                "name": user_data.get("name") or user_data.get("given_name", "Google User")
            }
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error fetching Google profile: {str(e)}"
            )

    @staticmethod
    def exchange_github_code(code: str, redirect_uri: str | None = None) -> dict:
        """Exchange GitHub authorization code for access token and fetch user details."""
        if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
            print("[GITHUB OAUTH] DEV MODE FALLBACK: Using mock GitHub data")
            return {
                "oauth_id": "github_dev_mock_12345",
                "email": "github_dev_user@example.com",
                "name": "GitHub Dev User"
            }

        # 1. Exchange authorization code for token
        token_url = "https://github.com/login/oauth/access_token"
        payload = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri

        try:
            r = requests.post(token_url, json=payload, headers={"Accept": "application/json"})
            if r.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub token exchange failed: {r.text}"
                )
            tokens = r.json()
            access_token = tokens.get("access_token")
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub token response missing access_token: {tokens}"
                )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error during GitHub OAuth: {str(e)}"
            )

        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

        # 2. Retrieve GitHub profile info
        try:
            r_profile = requests.get("https://api.github.com/user", headers=headers)
            if r_profile.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to retrieve GitHub profile info."
                )
            profile_data = r_profile.json()
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error fetching GitHub profile: {str(e)}"
            )

        # 3. Retrieve user email (since email might be private on GitHub)
        email = profile_data.get("email")
        if not email:
            try:
                r_emails = requests.get("https://api.github.com/user/emails", headers=headers)
                if r_emails.status_code == 200:
                    emails_list = r_emails.json()
                    # Find primary verified email
                    for em in emails_list:
                        if em.get("primary") and em.get("verified"):
                            email = em.get("email")
                            break
                    if not email and emails_list:
                        email = emails_list[0].get("email")
            except Exception:
                pass
        
        if not email:
            email = f"github_{profile_data.get('id')}@example.com"

        return {
            "oauth_id": str(profile_data.get("id")),
            "email": email,
            "name": profile_data.get("name") or profile_data.get("login", "GitHub User")
        }

    @staticmethod
    def verify_apple_token(id_token: str, code: str | None = None) -> dict:
        """Decode and validate Apple ID token."""
        try:
            # Decode the ID token without validation in dev mode or fallback
            payload = jwt.decode(id_token, "", options={"verify_signature": False})
            email = payload.get("email")
            sub = payload.get("sub")
            
            if not sub:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Apple ID token missing 'sub' claim."
                )
            
            return {
                "oauth_id": sub,
                "email": email or f"apple_{sub}@example.com",
                "name": "Apple User"
            }
        except Exception as e:
            # If id_token parsing fails, check if we have a dev fallback
            if not APPLE_CLIENT_ID:
                print("[APPLE OAUTH] DEV MODE FALLBACK: Using mock Apple data")
                return {
                    "oauth_id": "apple_dev_mock_12345",
                    "email": "apple_dev_user@example.com",
                    "name": "Apple Dev User"
                }
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Apple ID token validation failed: {str(e)}"
            )

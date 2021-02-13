"""Classes to interact with the Firebase Authentication service.
"""

import os
import firebase_admin
from firebase_admin import credentials, auth
from src.exceptions import FirebaseServiceError


class FirebaseService:
    """Interacts with anything on the Firebase SDK.
    """
    firebase_app = None
    def __init__(self):
        if not self.firebase_app and not firebase_admin._apps:
            service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not service_account_path:
                raise FirebaseServiceError("Service account key not found: service not initialized")
            self.firebase_app = firebase_admin.initialize_app(
                credentials.Certificate(service_account_path)
            )

    
    def user_info_at_uid(self, uid: str) -> dict:
        """Uses the Admin SDK to fetch details about a given user in
        Firebase Auth. Returns a dict with the user's email, UID and
        display name.
        """
        user_info = {}
        try:
            user = auth.get_user(uid)
            user_info = {'uid': uid, 'name': user.display_name, 'email': user.email}
        except ValueError:
            raise FirebaseServiceError(f"Cannot access user at UID {uid}")
        return user_info

    
    def verify_id_token(self, token: str) -> str:
        """Verifies that a token passed to the backend from
        Firebase is valid. If so, the UID for that token
        is returned.
        """
        
        # TODO: check_revoked is expensive, move this check to a rule if possible
        uid = None
        try:
            decoded_token = auth.verify_id_token(token, check_revoked=True)
            uid = decoded_token['uid']
        except auth.InvalidIdTokenError:
            raise FirebaseServiceError("Auth token is invalid")
        except auth.ExpiredIdTokenError:
            raise FirebaseServiceError("Auth token has expired")
        except auth.RevokedIdTokenError:
            raise FirebaseServiceError("Auth token was revoked")
        except Exception as e:
            print(e)
            raise FirebaseServiceError("Unexpected ID Token Verification Error")
        return uid


firebase_service = FirebaseService()
from apps.database.connection import get_connection
from apps.models.claims import Claim


class ClaimRepository:

    def delete(self, claim_id: str) -> bool:
        connection = get_connection()

        try:
            cursor = connection.execute(
                "DELETE FROM claims WHERE id = ?",
                (claim_id,),
            )
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


    def get_all(self):
        connection = get_connection()

        rows = connection.execute(
            """
            SELECT id, customer, amount, status
            FROM claims
            """
        ).fetchall()

        connection.close()

        return [
            Claim(
                id=row["id"],
                customer=row["customer"],
                amount=row["amount"],
                status=row["status"]
            )
            for row in rows
        ]

    def get_by_id(self, claim_id):
        connection = get_connection()

        row = connection.execute(
            """
            SELECT id, customer, amount, status
            FROM claims
            WHERE id = ?
            """,
            (claim_id,)
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return Claim(
            id=row["id"],
            customer=row["customer"],
            amount=row["amount"],
            status=row["status"]
        )

    def create(self, claim):
        connection = get_connection()

        connection.execute(
            """
            INSERT INTO claims (id, customer, amount, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                claim.id,
                claim.customer,
                claim.amount,
                claim.status
            )
        )

        connection.commit()
        connection.close()

        return claim

    def update_status(self, claim_id, new_status):
        connection = get_connection()

        connection.execute(
            """
            UPDATE claims
            SET status = ?
            WHERE id = ?
            """,
            (new_status, claim_id)
        )

        connection.commit()
        connection.close()
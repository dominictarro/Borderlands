/*
A procedure for granting the IAM user access to the Borderlands database.

1. Run the below script to create the RDS user and role in the Borderlands database.
2. Generate the user's temporary password
    `aws rds generate-db-auth-token --hostname <db cluster endpoint> --port 3306 --username Prefect`
3. Sign in to the database using the generated token
    `mysql -h <cluster endpoint> -u Prefect --password=<generated token> --enable-cleartext-plugin`

*/

-- Creates the RDS user that will be used by an IAM user to connect to the RDS instance
-- See Terraform file for the IAM user creation
CREATE USER IF NOT EXISTS 'Prefect'@'%' IDENTIFIED WITH AWSAuthenticationPlugin AS 'RDS';

-- Creates a role to perform expected operations on the Borderlands database
CREATE ROLE IF NOT EXISTS 'BorderlandsExecutor';
GRANT
    -- basic permissions
    SELECT,
    INSERT,
    UPDATE,
    DELETE,
    -- permissions for more complex routines
    CREATE TEMPORARY TABLES,
    EXECUTE,
    TRIGGER
ON Borderlands.* TO 'BorderlandsExecutor';

-- Grants the RDS user the necessary permissions to read and write to the Borderlands database
GRANT 'BorderlandsExecutor' TO 'Prefect';

// MongoDB initialization script
// This script runs when the MongoDB container is first created

// Switch to the clinic database
db = db.getSiblingDB('clinic_db');

// Create collections with schema validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['username', 'email', 'password_hash', 'role', 'created_at'],
      properties: {
        username: {
          bsonType: 'string',
          description: 'Must be a string and is required'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Must be a valid email address'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Hashed password is required'
        },
        role: {
          enum: ['admin', 'doctor', 'nurse', 'receptionist'],
          description: 'Role must be one of the allowed values'
        },
        is_active: {
          bsonType: 'bool',
          description: 'User active status'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('patients', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'email', 'phone', 'created_at'],
      properties: {
        name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100,
          description: 'Patient full name'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Valid email address'
        },
        phone: {
          bsonType: 'string',
          pattern: '^[0-9]{10,15}$',
          description: 'Phone number (digits only)'
        },
        date_of_birth: {
          bsonType: 'date',
          description: 'Patient date of birth'
        },
        address: {
          bsonType: 'object',
          properties: {
            street: { bsonType: 'string' },
            city: { bsonType: 'string' },
            state: { bsonType: 'string' },
            zip_code: { bsonType: 'string' }
          }
        },
        medical_record_number: {
          bsonType: 'string',
          description: 'External medical record number'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

db.createCollection('appointments', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['patient_id', 'scheduled_at', 'duration_minutes', 'status', 'created_at'],
      properties: {
        patient_id: {
          bsonType: 'objectId',
          description: 'Reference to patient'
        },
        provider_id: {
          bsonType: 'objectId',
          description: 'Reference to healthcare provider (user)'
        },
        scheduled_at: {
          bsonType: 'date',
          description: 'Appointment date and time'
        },
        duration_minutes: {
          bsonType: 'int',
          minimum: 15,
          maximum: 240,
          description: 'Appointment duration in minutes'
        },
        type: {
          enum: ['consultation', 'follow-up', 'procedure', 'emergency'],
          description: 'Type of appointment'
        },
        status: {
          enum: ['scheduled', 'confirmed', 'in-progress', 'completed', 'cancelled', 'no-show'],
          description: 'Current appointment status'
        },
        notes: {
          bsonType: 'string',
          description: 'Additional notes'
        },
        created_at: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

// Create indexes for better query performance
db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'username': 1 }, { unique: true });
db.users.createIndex({ 'role': 1 });

db.patients.createIndex({ 'email': 1 }, { unique: true });
db.patients.createIndex({ 'phone': 1 });
db.patients.createIndex({ 'name': 'text' });

db.appointments.createIndex({ 'patient_id': 1 });
db.appointments.createIndex({ 'provider_id': 1 });
db.appointments.createIndex({ 'scheduled_at': 1 });
db.appointments.createIndex({ 'status': 1 });
db.appointments.createIndex({ 'scheduled_at': 1, 'status': 1 });

// Create a default admin user (password: admin123)
// Note: In production, change this password immediately
db.users.insertOne({
  username: 'admin',
  email: 'admin@clinicapp.com.br',
  password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCfiyB/yK',
  role: 'admin',
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
});

print('MongoDB initialization completed successfully!');